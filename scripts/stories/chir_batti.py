"""Builds queue/004-chir-batti.json (Tall-Tale Original #3). Run: python scripts/stories/chir_batti.py

Chir batti: lights reported over the Banni grasslands and the Great Rann of Kutch on dark nights.
Unexplained (marsh gas is one guess). Characters and plot are fiction.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
N = "narrator"

characters = [
    {"id": "kanji", "name": "Kanji", "role": "child_boy", "gender": "male", "voice": "hi-IN-MadhurNeural",
     "look": "thin Indian boy aged 10 from Kutch, short black hair, sun-tanned skin, white frilled kediyu top, "
             "white dhoti, a small red cloth tied on his head"},
    {"id": "raghu", "name": "Raghu Dada", "role": "old_man", "gender": "male", "voice": "hi-IN-MadhurNeural",
     "look": "Indian herder aged 70 from Kutch, big curled white moustache, white turban, white frilled kediyu, "
             "white dhoti, holding a dark wooden walking stick"},
    {"id": "jeevi", "name": "Jeevi", "role": "young_woman", "gender": "female", "voice": "hi-IN-SwaraNeural",
     "look": "Indian woman aged 35 from Kutch, black odhni with small round mirror-work, red embroidered skirt, "
             "silver bangles, hair under the odhni"},
    {"id": "hamir", "name": "Hamir", "role": "authority", "gender": "male", "voice": "hi-IN-MadhurNeural",
     "look": "Indian herder aged 40 from Kutch, thick black moustache, white turban, white frilled kediyu, "
             "white dhoti, long wooden herder's staff"},
    {"id": "light", "name": "The Light (chir batti)", "role": "ghost", "gender": "female", "voice": "hi-IN-SwaraNeural",
     "eleven_settings": {"stability": 0.8, "style": 0.05},
     "look": "a floating ball of pale blue-white light the size of a lantern, glowing softly, hovering low over the "
             "ground, no body, no face"},
]

props = [
    {"id": "bell", "look": "a dented brass buffalo bell hanging on a braided black cord"},
    {"id": "kali", "look": "a big black Banni buffalo with long curved horns and a braided black cord round its neck"},
]

V = "a Maldhari herders' village of round white mud huts with conical thatched roofs in the Banni grasslands of Kutch, Gujarat"
R = "the Great Rann of Kutch, an endless flat white salt desert with cracked hexagon patterns"
NIGHT = "moonless night, black sky full of stars"

# (id, setting, characters, mood, props, continuity, [(speaker, hindi, english[, shot])])
scenes = [
    ("s01", f"{R}, {NIGHT}, three pale blue-white lights floating low over the salt", ["light"], "dread", [], "", [
        (N, "कच्छ के रण में अगर रात को कोई रोशनी तुम्हारा नाम पुकारे… उसके पीछे मत जाना।",
         "In the Rann of Kutch, if a light calls your name at night… don't follow it."),
        (N, "यहाँ के लोग उसे चिर बत्ती कहते हैं। वो रोशनी जो चलती है।",
         "The people here call it chir batti. The light that walks.",
         "three glowing pale blue balls of light drifting over a white salt desert under stars"),
        (N, "कहते हैं, जो उसके पीछे गया, रण ने उसे कभी वापस नहीं किया।",
         "They say whoever followed it was never given back by the Rann."),
        ("light", "कानजी… कानजी… इधर आओ।", "Kanji… Kanji… come here."),
        (N, "और उस साल, वो रोशनी एक दस साल के लड़के का नाम ले रही थी।",
         "And that year, the light was calling the name of a ten-year-old boy."),
    ]),
    ("s02", f"{V} at sunset, round mud huts, buffaloes grazing on dry grass, a boy standing at the edge looking "
            "towards the white horizon", ["kanji"], "calm", [], "", [
        (N, "बन्नी के घास के मैदान। गोल मिट्टी के घर, जिन्हें भूंगा कहते हैं।",
         "The grasslands of Banni. Round mud houses called bhungas."),
        (N, "यहाँ मालधारी रहते हैं। भैंसों के साथ, रण के किनारे।",
         "The Maldhari herders live here. With their buffaloes, at the edge of the Rann."),
        (N, "हर शाम दस साल का कानजी गाँव के आख़िरी घर पर खड़ा होकर रण की तरफ़ देखता था।",
         "Every evening, ten-year-old Kanji stood at the last house and stared at the Rann.",
         "a boy in a white frilled top standing alone at the edge of a grassland, white salt horizon beyond"),
        (N, "क्योंकि तीन रात पहले, उसके बापू उसी तरफ़ गए थे… और लौटे नहीं।",
         "Because three nights ago, his father had gone that way… and had not come back."),
    ]),
    ("s03", f"inside a round mud hut of {V} at dusk, a worried woman, an old man and a boy sitting by a small fire",
     ["jeevi", "raghu", "kanji"], "piano", [], "", [
        (N, "उस रात उनकी सबसे अच्छी भैंस, काली, रस्सी तोड़कर रण की तरफ़ भाग गई थी।",
         "That night their best buffalo, Kali, had broken her rope and run towards the Rann."),
        (N, "हमीर, कानजी के बापू, लाठी उठाकर उसके पीछे गए थे।",
         "Hamir, Kanji's father, had picked up his staff and gone after her."),
        ("jeevi", "तीन दिन हो गए। गाँव वाले कहते हैं, अब ढूँढना बेकार है।",
         "It's been three days. The villagers say there's no use searching now."),
        ("kanji", "बापू ज़िंदा हैं, माँ। मुझे पता है।", "Baba is alive, Ma. I know it."),
        (N, "रघु दादा चुप रहे। उन्होंने बस दरवाज़े की तरफ़ देखा, जहाँ से रण दिखता था।",
         "Raghu Dada said nothing. He only looked at the door, through which the Rann could be seen."),
    ]),
    ("s04", f"inside the mud hut at night, an old man telling a story by a small fire, a boy listening wide-eyed",
     ["raghu", "kanji"], "drone", [], "", [
        ("raghu", "सुन, कानजी। रण में अमावस की रातों को रोशनियाँ चलती हैं।",
         "Listen, Kanji. On moonless nights, lights walk in the Rann."),
        ("raghu", "पहले दूर दिखती हैं। फिर पास आती हैं। फिर किसी का नाम लेती हैं।",
         "First they're far away. Then they come closer. Then they call someone's name."),
        ("kanji", "किसका नाम, दादा?", "Whose name, Dada?"),
        ("raghu", "जिसे वो ले जाना चाहती हैं। और जिन्हें वो ले जा चुकीं… उनकी आवाज़ में बोलती हैं।",
         "Whoever they want to take. And they speak… in the voices of the ones they've already taken."),
        (N, "आग की लौ काँपी। बाहर, बहुत दूर, रण पर कुछ चमका।",
         "The flame flickered. Outside, far away, something glowed on the Rann.",
         "through a round hut's doorway, a tiny blue light glowing far away on a dark white desert"),
    ]),
    ("s05", f"the edge of {V} at night facing {R}, {NIGHT}, a boy standing alone, a blue light far out on the salt",
     ["kanji", "light"], "dread", [], "", [
        (N, "आधी रात को कानजी की नींद खुली। किसी ने बाहर से पुकारा था।",
         "At midnight Kanji woke up. Someone had called from outside."),
        ("hamir", "कानजी… कानजी, बेटा… मैं यहाँ हूँ!", "Kanji… Kanji, son… I'm here!", "a single pale blue light glowing far away on a dark white salt desert, seen from a hut door"),
        (N, "बापू की आवाज़। वही आवाज़, जो हर सुबह उसे जगाती थी।",
         "Baba's voice. The same voice that woke him every morning."),
        ("kanji", "बापू! बापू, मैं आ रहा हूँ!", "Baba! Baba, I'm coming!",
         "a barefoot boy running from the mud huts towards a glowing blue light on a white desert at night"),
        (N, "वो नंगे पाँव रण की तरफ़ दौड़ा।", "He ran barefoot towards the Rann."),
    ]),
    ("s06", f"the edge of {R} at night, an old man with a walking stick grabbing a boy by the arm, a blue light ahead",
     ["raghu", "kanji", "light"], "chase", [], "", [
        (N, "एक झटके में किसी ने उसका हाथ पकड़ लिया। रघु दादा।",
         "In a jerk, someone caught his arm. Raghu Dada."),
        ("raghu", "रुक जा! वो तेरे बापू नहीं हैं!", "Stop! That is not your father!"),
        ("kanji", "पर दादा, वो बापू की आवाज़ है!", "But Dada, that's Baba's voice!"),
        ("raghu", "हाँ। इसीलिए तो डर है।", "Yes. That's exactly why I'm afraid."),
        (N, "दूर रोशनी एक पल रुकी। जैसे उसने उन्हें सुन लिया हो। फिर धीरे-धीरे बुझ गई।",
         "The far light paused for a moment. As if it had heard them. Then it slowly went out."),
    ]),
    ("s07", "inside the mud hut at dawn, an old man showing a boy a dented brass buffalo bell", ["raghu", "kanji"],
     "piano", ["bell"], "", [
        (N, "सुबह रघु दादा ने कानजी को अपने पास बिठाया।", "In the morning, Raghu Dada sat Kanji down beside him."),
        ("raghu", "एक बात याद रख। वो रोशनी हर आवाज़ की नक़ल कर सकती है। इंसान की, जानवर की।",
         "Remember one thing. That light can copy every voice. A man's, an animal's."),
        ("raghu", "पर पीतल की नहीं। घंटी की आवाज़ असली होती है।",
         "But not brass. The sound of a bell is always real."),
        (N, "उन्होंने एक पुरानी पीतल की घंटी उसके हाथ में रखी।", "He placed an old brass bell in his hand.",
         "close-up of an old wrinkled hand placing a dented brass bell in a small boy's palm"),
        ("raghu", "काली के गले में भी ऐसी ही घंटी थी। तेरे बापू ने ख़ुद बाँधी थी।",
         "Kali wore a bell just like this on her neck. Your father tied it himself."),
        ("kanji", "तो अगर बापू काली के पास हैं… तो घंटी बजेगी।", "So if Baba is with Kali… the bell will ring."),
    ]),
    ("s08", f"{V} in afternoon heat, villagers shaking their heads, a woman crying at a hut door", ["jeevi", "kanji"],
     "drone", [], "", [
        (N, "उस दिन गाँव के आदमी फिर रण में गए। शाम को ख़ाली हाथ लौटे।",
         "That day the village men went into the Rann again. They came back empty-handed at dusk."),
        ("jeevi", "बस अब कोई नहीं जाएगा। रण ने एक ले लिया है। दूसरा नहीं दूँगी।",
         "No one else goes now. The Rann has taken one. I won't give it another."),
        (N, "उसने कानजी को सीने से लगा लिया। पर कानजी की आँखें रण पर थीं।",
         "She held Kanji to her chest. But Kanji's eyes were on the Rann."),
    ]),
    ("s09", f"the doorway of a mud hut in {V} at night, a boy slipping out quietly with a brass bell, {NIGHT}",
     ["kanji"], "dread", ["bell"], "the boy holds the brass bell in his hand", [
        (N, "दूसरी अमावस की रात। सब सो गए थे।", "The second moonless night. Everyone was asleep."),
        (N, "कानजी ने घंटी कपड़े में लपेटी, ताकि आवाज़ न हो, और चुपके से बाहर निकल गया।",
         "Kanji wrapped the bell in cloth so it wouldn't ring, and slipped outside."),
        (N, "सामने रण था। सफ़ेद, ख़ामोश, और अंतहीन।", "Ahead was the Rann. White, silent and endless.",
         "a small boy from behind, standing at the edge of an endless white salt desert under a starry sky"),
        ("kanji", "बापू, मैं आ रहा हूँ।", "Baba, I'm coming."),
    ]),
    ("s10", f"{R}, {NIGHT}, a small boy walking alone on the cracked white salt, faint blue lights far away",
     ["kanji", "light"], "drone", ["bell"], "the boy holds the brass bell", [
        (N, "रण में अँधेरा भी सफ़ेद होता है। नमक तारों की रोशनी पकड़ लेता है।",
         "In the Rann even the dark is white. The salt catches the starlight."),
        (N, "कानजी चलता गया। गाँव की आख़िरी रोशनी पीछे छूट गई।",
         "Kanji kept walking. The village's last light was left behind."),
        (N, "फिर सामने, दूर, एक नीली रोशनी जली। फिर दूसरी। फिर तीसरी।",
         "Then ahead, far away, a blue light glowed. Then a second. Then a third.",
         "three pale blue lights appearing one by one on a dark horizon of white salt"),
        (N, "वो धीरे-धीरे उसकी तरफ़ आने लगीं।", "Slowly, they began to move towards him."),
    ]),
    ("s11", f"{R}, {NIGHT}, blue lights circling a frightened boy on the salt", ["kanji", "light"], "pulse", ["bell"],
     "the boy clutches the brass bell", [
        ("jeevi", "कानजी! कानजी, घर आ जा, बेटा! मैं यहाँ हूँ!", "Kanji! Kanji, come home, son! I'm here!", "a pale blue light hovering behind a frightened boy on white salt at night"),
        (N, "माँ की आवाज़। ठीक उसके पीछे से।", "Ma's voice. Right behind him."),
        ("kanji", "माँ? पर माँ तो घर पर सो रही है…", "Ma? But Ma is asleep at home…"),
        ("raghu", "कानजी, इधर आ। रास्ता इधर है।", "Kanji, come here. The way is here.", "a pale blue light floating to the left in the dark over cracked salt"),
        (N, "अब दादा की आवाज़। बाईं तरफ़ से। पर दादा भी तो घर पर थे।",
         "Now Dada's voice. From the left. But Dada was at home too.",
         "a boy turning in fear as glowing blue lights circle him on white salt"),
        (N, "कानजी समझ गया। ये वही रोशनियाँ थीं।", "Kanji understood. These were the lights."),
    ]),
    ("s12", f"{R}, {NIGHT}, a man-shaped figure made of pale blue light walking towards a boy, the boy's shadow on the "
            "salt but no shadow under the figure", ["kanji", "light"], "reveal", ["bell"], "", [
        (N, "फिर सामने से कोई चलकर आया। सफ़ेद पगड़ी। लंबी लाठी।",
         "Then someone walked towards him. A white turban. A long staff."),
        ("hamir", "कानजी… मेरे बेटे… चल, घर चलते हैं।", "Kanji… my son… come, let's go home.", "a tall figure made of pale blue light shaped like a man in a turban with a staff, walking over white salt"),
        (N, "बापू। बिल्कुल बापू जैसे। वही चाल, वही आवाज़।", "Baba. Exactly like Baba. The same walk, the same voice."),
        (N, "कानजी आगे बढ़ा… और रुक गया।", "Kanji stepped forward… and stopped."),
        (N, "नमक पर कानजी की परछाईं थी। पर बापू के पैरों के नीचे… कोई परछाईं नहीं थी।",
         "On the salt lay Kanji's shadow. But under Baba's feet… there was no shadow at all.",
         "close-up of white cracked salt, a boy's shadow on it, and beside it a man's bare feet with no shadow"),
    ]),
    ("s13", f"{R}, {NIGHT}, a boy with eyes shut tight, ears straining, blue light figure in front of him",
     ["kanji", "light"], "dread", ["bell"], "", [
        (N, "कानजी ने आँखें बंद कर लीं। दादा की बात याद आई।", "Kanji shut his eyes. He remembered Dada's words."),
        (N, "हर आवाज़ झूठी हो सकती है। पीतल की नहीं।", "Every voice can lie. Brass cannot."),
        ("hamir", "आँखें खोल, कानजी। अपने बापू को देख।", "Open your eyes, Kanji. Look at your father.", "a glowing blue man-shaped light leaning over a small boy who keeps his eyes shut"),
        (N, "उसने सुना। हवा। अपनी धड़कन। उस आवाज़ की फुसफुसाहट।",
         "He listened. The wind. His own heartbeat. The whisper of that voice."),
        (N, "और फिर… बहुत दूर, दाईं तरफ़ से… टन्न… टन्न।", "And then… very far away, from the right… clang… clang."),
        (N, "एक घंटी।", "A bell."),
    ]),
    ("s14", f"{R}, {NIGHT}, a boy running away from the blue lights towards the dark right side, holding his bell",
     ["kanji", "light"], "chase", ["bell"], "", [
        (N, "कानजी ने रोशनी से मुँह फेरा और घंटी की आवाज़ की तरफ़ दौड़ा।",
         "Kanji turned away from the light and ran towards the sound of the bell."),
        ("hamir", "कानजी! उधर मत जा! वहाँ अँधेरा है!", "Kanji! Don't go that way! It's dark there!", "blue lights streaking after a running boy across dark salt"),
        (N, "पीछे से बापू की आवाज़ चीख़ी। फिर माँ की। फिर दादा की। सब एक साथ।",
         "Behind him Baba's voice screamed. Then Ma's. Then Dada's. All at once.",
         "a small boy running through darkness on salt, many blue lights chasing behind him"),
        (N, "कानजी नहीं रुका। टन्न… टन्न… आवाज़ पास आती गई।",
         "Kanji didn't stop. Clang… clang… the sound grew closer."),
    ]),
    ("s15", f"a deep crack in the salt crust of {R} at night, a black buffalo standing beside it, an injured man lying "
            "in the crack", ["kanji", "hamir"], "reveal", ["kali", "bell"],
     "the black buffalo stands at the edge of the salt crack", [
        (N, "और वहाँ, नमक की एक गहरी दरार के किनारे… काली खड़ी थी। गले में घंटी।",
         "And there, at the edge of a deep crack in the salt… stood Kali. The bell on her neck.",
         "a big black buffalo with curved horns standing at the edge of a crack in white salt at night"),
        (N, "और दरार में, पैर पर कपड़ा बाँधे, पड़े थे… बापू।",
         "And in the crack, a cloth tied around his leg, lay… Baba."),
        ("kanji", "बापू!", "Baba!"),
        ("hamir", "कानजी? तू… तू सच में है?", "Kanji? Are you… are you really here?"),
        ("hamir", "तीन रात से वो रोशनियाँ तेरी आवाज़ में मुझे बुला रही थीं।",
         "For three nights those lights have been calling me in your voice."),
        ("hamir", "मैं नहीं गया। काली ने हिलने नहीं दिया। वो मुझे छोड़कर नहीं गई।",
         "I didn't go. Kali wouldn't let me move. She never left me."),
    ]),
    ("s16", f"the salt crack in {R} at night, a boy helping his limping father up, blue lights gathering in a ring "
            "around them", ["kanji", "hamir", "light"], "pulse", ["kali", "bell"], "", [
        (N, "कानजी ने बापू को सहारा देकर बाहर निकाला।", "Kanji helped his father climb out."),
        (N, "पर तब तक, चारों तरफ़ रोशनियाँ जमा हो चुकी थीं। एक घेरा।",
         "But by then the lights had gathered all around them. A ring.",
         "a ring of glowing blue lights surrounding a boy, a limping man and a black buffalo on white salt"),
        ("hamir", "रोशनी को मत देखना, बेटा। आँखें ज़मीन पर। कान घंटी पर।",
         "Don't look at the light, son. Eyes on the ground. Ears on the bell."),
        ("kanji", "और रास्ता?", "And the way?"),
        ("hamir", "काली जानती है। जानवर कभी झूठी आवाज़ के पीछे नहीं जाते।",
         "Kali knows it. Animals never follow a false voice."),
    ]),
    ("s17", f"{R} at night, a boy ringing a brass bell, a limping man holding a buffalo's cord, walking with heads "
            "down while blue lights follow", ["kanji", "hamir", "light"], "drone", ["kali", "bell"],
     "the boy rings the brass bell as they walk", [
        (N, "वो चल पड़े। आगे काली। पीछे बापू। बीच में कानजी, घंटी बजाते हुए।",
         "They set off. Kali in front. Baba behind. Kanji in the middle, ringing the bell."),
        (N, "टन्न… टन्न… हर क़दम पर।", "Clang… clang… with every step.",
         "close-up of a small hand ringing a dented brass bell"),
        ("jeevi", "हमीर… रुक जाओ… मैं यहाँ हूँ, पीछे देखो…", "Hamir… stop… I'm here, look behind you…", "pale blue lights following behind two walking figures and a buffalo on white salt"),
        ("raghu", "बेटा, ग़लत रास्ता है… इधर आओ…", "Son, it's the wrong way… come this way…", "a blue light drifting close beside walking feet on cracked salt"),
        (N, "रोशनियाँ पीछे-पीछे आती रहीं। हर उस आवाज़ में बोलती हुई, जिसे वो जानती थीं।",
         "The lights kept following. Speaking in every voice they knew."),
    ]),
    ("s18", f"{R} at night, a boy and his father walking with eyes down, a blue light hovering right beside the boy's ear",
     ["kanji", "hamir", "light"], "dread", ["kali", "bell"], "", [
        (N, "और फिर एक आवाज़ आई जिसने बापू के क़दम रोक दिए।", "And then came a voice that stopped Baba in his tracks."),
        ("kanji", "बापू… मैं यहाँ हूँ… पीछे… आपने मुझे छोड़ दिया…",
         "Baba… I'm here… behind you… you left me behind…",
         "a pale blue light hovering behind a man's shoulder in the dark"),
        (N, "कानजी की आवाज़। पीछे से। जबकि कानजी उनके हाथ को पकड़े खड़ा था।",
         "Kanji's voice. From behind. While Kanji stood right there, holding his hand."),
        ("kanji", "बापू, वो मैं नहीं हूँ! मैं यहाँ हूँ! घंटी सुनो!",
         "Baba, that's not me! I'm here! Listen to the bell!"),
        (N, "कानजी ने पूरी ताक़त से घंटी बजाई। टन्न! टन्न! टन्न!",
         "Kanji rang the bell with all his strength. Clang! Clang! Clang!"),
    ]),
    ("s19", f"the edge of {V} at first light, a pale dawn over {R}, a woman and an old man running towards a boy, "
            "his limping father and a black buffalo", ["jeevi", "raghu", "kanji", "hamir"], "reveal", ["kali", "bell"],
     "", [
        (N, "पूरब में आसमान फीका पड़ने लगा। रोशनियाँ एक-एक करके बुझ गईं।",
         "The sky in the east began to pale. The lights went out one by one."),
        (N, "और गाँव के किनारे, माँ और दादा ने देखा… रण से तीन परछाइयाँ लौट रही थीं।",
         "And at the village edge, Ma and Dada saw… three shadows returning from the Rann.",
         "silhouettes of a boy, a limping man and a buffalo walking out of a white desert at dawn"),
        ("jeevi", "हमीर! कानजी!", "Hamir! Kanji!"),
        ("raghu", "पीतल ने झूठ नहीं बोला।", "The brass didn't lie."),
        (N, "उस सुबह बन्नी के एक भूंगे में बरसों बाद सब एक साथ हँसे।",
         "That morning, in one bhunga of Banni, everyone laughed together for the first time in years."),
    ]),
    ("s20", f"inside the mud hut at night, a family asleep by a dying fire, a man waking up, a pale blue glow at the "
            "small window", ["hamir", "kanji", "light"], "dread", ["bell"],
     "the brass bell hangs on a nail by the boy's bed", [
        (N, "उस रात सब थककर सो गए।", "That night everyone slept, exhausted."),
        (N, "आधी रात को खिड़की पर एक नीली चमक आई।", "At midnight, a blue glow appeared at the window.",
         "a small round hut window with a pale blue glow outside in the dark"),
        ("kanji", "बापू… बापू, मैं बाहर हूँ… दरवाज़ा खोलो…", "Baba… Baba, I'm outside… open the door…", "blue light leaking through the cracks of a wooden hut door at night"),
        (N, "कानजी की आवाज़। बाहर से।", "Kanji's voice. From outside."),
        (N, "हमीर नींद में उठे। दरवाज़े की तरफ़ बढ़े। उनका हाथ कुंडी तक पहुँचा…",
         "Hamir rose, half asleep. He moved to the door. His hand reached the latch…",
         "a man's hand reaching for a wooden door latch in a dark hut, blue light in the cracks"),
    ]),
    ("s21", f"inside the mud hut at night, a boy sitting up in bed ringing a brass bell, the blue glow at the window "
            "fading", ["kanji", "hamir", "light"], "reveal", ["bell"], "", [
        (N, "तभी, अंदर से… टन्न।", "Then, from inside… clang."),
        (N, "कानजी अपने बिस्तर पर बैठा था। हाथ में घंटी।", "Kanji was sitting up in his bed. The bell in his hand.",
         "a boy sitting up in bed in the dark, ringing a brass bell, looking straight at his father"),
        ("kanji", "बापू। मैं यहाँ हूँ।", "Baba. I'm here."),
        (N, "बाहर की नीली रोशनी काँपी… और बुझ गई।", "The blue light outside trembled… and went out."),
        (N, "रण में आज भी अमावस की रातों को रोशनियाँ चलती हैं। वैज्ञानिक कहते हैं, शायद दलदल की गैस है।",
         "On moonless nights the lights still walk in the Rann. Scientists say it may be marsh gas."),
        (N, "पर बन्नी के हर घर में, आज भी, दरवाज़े के पास एक पीतल की घंटी टँगी रहती है।",
         "But in every home in Banni, even today, a brass bell hangs beside the door.",
         "a dented brass bell hanging on a nail beside a mud hut door, a faint blue glow far outside"),
    ]),
]

story = {
    "id": "004-chir-batti",
    "title": "रण की वो रोशनी… जो नाम लेकर बुलाती है 😱 | Chir Batti | Hindi Horror Story",
    "genre": "horror",
    "art_style": "creepy_comic",
    "language": "hi",
    "logline": "In the Rann of Kutch, ghost lights call people in the voices of the ones they took. A ten-year-old "
               "herder's son walks into the salt desert with a brass bell to bring his father home.",
    "characters": characters,
    "props": props,
    "scenes": [
        {"id": sid, "setting": setting, "characters": chars, "mood": mood,
         **({"props": pr} if pr else {}), **({"continuity": cont} if cont else {}),
         "lines": [{"speaker": l[0], "text": l[1], "en": l[2], **({"shot": l[3]} if len(l) > 3 else {})}
                   for l in lines]}
        for sid, setting, chars, mood, pr, cont, lines in scenes
    ],
    "thumbnail": {
        "prompt": "a small boy in a white frilled top standing alone on a vast white salt desert at night holding a "
                  "brass bell, a glowing blue man-shaped light with no shadow reaching towards him",
        "text": "पीछे मत जाना",
    },
    "shorts": [
        {"scenes": ["s01", "s05"], "title": "रण में ये रोशनी आपका नाम लेती है 😱 | Chir Batti",
         "hook": "three pale blue lights drifting over a white salt desert at night"},
        {"scenes": ["s07"], "title": "हर आवाज़ झूठ बोल सकती है, ये नहीं 😱 | Chir Batti",
         "hook": "a dented brass bell placed in a small boy's palm by an old hand"},
        {"scenes": ["s12", "s13"], "title": "बापू आए… पर उनकी परछाईं नहीं थी 😱 | Chir Batti",
         "hook": "a boy's shadow on white salt beside a man's feet with no shadow"},
        {"scenes": ["s20", "s21"], "title": "रात को बाहर से मेरी आवाज़ आई 😱 | Chir Batti",
         "hook": "a pale blue glow at a small round hut window at night"},
    ],
    "youtube": {
        "description": "In the Banni grasslands at the edge of the Great Rann of Kutch, herders tell of chir batti: "
                       "lights that walk across the salt on moonless nights and call people by name, in the voices "
                       "of those they have already taken. When his father disappears into the Rann chasing a lost "
                       "buffalo, ten-year-old Kanji walks out into the white desert with nothing but a brass bell.\n\n"
                       "Chir batti is a real local legend of Kutch. The characters and events in this story are fiction.",
        "hashtags": ["#ChirBatti", "#RannOfKutch"],
        "tags": ["chir batti", "chir batti kutch", "rann of kutch horror", "kutch ghost lights", "gujarat horror story",
                 "banni grassland", "bhoot ki kahani", "darawani kahani", "horror story in hindi",
                 "hindi horror story"],
    },
}

out = ROOT / "queue" / f"{story['id']}.json"
out.write_text(json.dumps(story, indent=2, ensure_ascii=False), encoding="utf-8")
print("wrote", out)
