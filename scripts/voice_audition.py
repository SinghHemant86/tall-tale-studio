"""Render short Hindi test lines for candidate voices, so a human can listen and choose.
Writes voice-audition/<role>__<label>.mp3 and index.json. Uses ELEVENLABS_API_KEY (env)."""
import json, os, subprocess, sys, time
from pathlib import Path
import requests

OUT = Path("voice-audition"); OUT.mkdir(exist_ok=True)
KEY = os.environ["ELEVENLABS_API_KEY"].strip()
MODEL = "eleven_multilingual_v2"

LINES = {
 "harry":    "मैं चोर ज़रूर हूँ काका, पर सिर्फ़ सुराग़ चुराता हूँ। केस ख़त्म, नट शुरू!",
 "gajju":    "सॉरी अंकल… बस एक और पैकेट… दादी को बुखार है, और वो सिर्फ़ नूडल्स खाती हैं।",
 "rangeeli": "लोग देखते ही फ़ैसला कर लेते हैं, हैरी।",
 "balwant":  "हटो हटो! पुलिस आ गई! चलिए थाने!",
 "totaram":  "चिट्ठी! चिट्ठी! और हाँ हैरी, कल रात गली में किसी की आवाज़ सुनी।",
 "kaka":     "हैरी बेटा, आज सुबह-सुबह कोई केस नहीं मिला?",
 "narrator": "नुक्कड़ नगर। यहाँ इंसान और जानवर साथ रहते हैं, साथ बस में सफ़र करते हैं, और साथ चाय पीते हैं।",
}
# (role, label, voice_id, pitch_up_percent)
C = [
 ("harry","Viraj warm-lively","iWNf11sz1GrUE4ppxTOL",0),
 ("harry","Viraj clear-narrator","FmBhnvP58BK0vz65OOj7",0),
 ("harry","Viraj expressive","3AMU7jXQuQa3oRvRqUmb",0),
 ("harry","Abhii energetic","tVeibrRmkweME2rrFZAs",0),
 ("harry","Bunty reel","FZkK3TvQ0pjyDmT8fzIW",0),
 ("harry","Viraj warm-lively +10% pitch","iWNf11sz1GrUE4ppxTOL",10),
 ("harry","Abhii +10% pitch","tVeibrRmkweME2rrFZAs",10),
 ("gajju","Saanu (current kid voice)","d9BvEI0bp2Tmdpqnjwn0",0),
 ("gajju","Simran bright","TRnaQb7q41oL7sV0w6Bu",0),
 ("gajju","Anika sweet","RABOvaPec1ymXz02oDQi",0),
 ("gajju","Anika animated","Sm1seazb4gs7RSlUVw7c",0),
 ("gajju","Abhii +15% pitch","tVeibrRmkweME2rrFZAs",15),
 ("gajju","Simran +8% pitch","TRnaQb7q41oL7sV0w6Bu",8),
 ("rangeeli","Muskaan calm-inviting","xoV6iGVuOGYHLWjXhVC7",0),
 ("rangeeli","Simran bright","TRnaQb7q41oL7sV0w6Bu",0),
 ("rangeeli","Saavi warm","81xnrLNObbKDEs179emP",0),
 ("rangeeli","Devi (current woman)","kdkz0RPvRYjuZ1OqDPeY",0),
 ("balwant","Ranga bold","d0grukerEzs069eKIauC",0),
 ("balwant","Krishna energetic","m5qndnI7u4OAdXhH0Mr5",0),
 ("balwant","Leo inviting","IvLWq57RKibBrqZGpQrC",0),
 ("balwant","Jeet Bihari raw","3Th96YoTP1kEKxJroYo1",0),
 ("totaram","Bunty funny friend","7b9mYhmnp0y2qSH1FnBL",0),
 ("totaram","Leo inviting","IvLWq57RKibBrqZGpQrC",0),
 ("totaram","Raju young warm","eyVoIoi3vo6sJoHOKgAc",0),
 ("totaram","Bunty +10% pitch","7b9mYhmnp0y2qSH1FnBL",10),
 ("kaka","Raju warm","zT03pEAEi0VHKciJODfn",0),
 ("kaka","Arun village uncle","ZjpoNq7arSoRlQKCzAEL",0),
 ("kaka","Amit Gupta sympathetic","Sxk6njaoa7XLsAFT7WcN",0),
 ("narrator","Anjali soothing","gHu9GtaHOXcSqFTK06ux",0),
 ("narrator","Muskaan friendly","xoV6iGVuOGYHLWjXhVC7",0),
 ("narrator","Raju clear","zT03pEAEi0VHKciJODfn",0),
]
index, fails = [], []
for role, label, vid, pitch in C:
    safe = label.replace(" ", "_").replace("+", "p").replace("%", "").replace("(", "").replace(")", "").replace("-", "_")
    f = OUT / f"{role}__{safe}.mp3"
    r = requests.post(f"https://api.elevenlabs.io/v1/text-to-speech/{vid}?output_format=mp3_44100_128",
                      headers={"xi-api-key": KEY, "accept": "audio/mpeg"},
                      json={"text": LINES[role], "model_id": MODEL,
                            "voice_settings": {"stability": 0.45, "similarity_boost": 0.8, "style": 0.4, "use_speaker_boost": True}},
                      timeout=120)
    if r.status_code >= 400:
        fails.append((role, label, vid, r.status_code, r.text[:160])); print("FAIL", role, label, r.status_code, r.text[:160]); continue
    raw = f.with_suffix(".raw.mp3"); raw.write_bytes(r.content)
    if pitch:
        k = 1 + pitch / 100
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(raw), "-af",
                        f"asetrate=44100*{k},aresample=44100,atempo={1/k:.4f}", str(f)], check=True)
        raw.unlink()
    else:
        raw.rename(f)
    index.append({"role": role, "label": label, "voice_id": vid, "pitch_up": pitch, "file": f.name, "line": LINES[role]})
    print("ok", role, label); time.sleep(0.4)
(OUT / "index.json").write_text(json.dumps({"clips": index, "failed": fails}, ensure_ascii=False, indent=1))
