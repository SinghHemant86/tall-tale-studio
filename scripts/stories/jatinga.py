"""Builds queue/003-jatinga.json (Tall-Tale Original #2). Run: python scripts/stories/jatinga.py

Jatinga (Dima Hasao, Assam) is a real village known for birds diving into lights on foggy, moonless
nights. The characters and plot are fiction; the science and the village's conservation turn are real.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
N = "narrator"

characters = [
    {"id": "meera", "name": "Meera", "role": "young_woman", "gender": "female", "voice": "hi-IN-SwaraNeural",
     "look": "Indian woman aged 28, jaw-length straight black hair, olive green field jacket over a grey t-shirt, "
             "dark blue jeans, a black camera on a strap around her neck"},
    {"id": "phrang", "name": "Bah Phrang", "role": "old_man", "gender": "male", "voice": "hi-IN-MadhurNeural",
     "look": "thin Northeast Indian man aged 70, short cropped white hair, clean-shaven deeply wrinkled face, "
             "maroon-and-white checked woollen shawl over a grey sweater"},
    {"id": "phrang_young", "name": "Phrang (1988)", "role": "friend", "gender": "male", "voice": "hi-IN-MadhurNeural",
     "look": "Northeast Indian man aged 32, short black hair, thin moustache, maroon-and-white checked woollen "
             "shawl over a grey sweater, 1988"},
    {"id": "iba", "name": "Iba", "role": "child_girl", "gender": "female", "voice": "hi-IN-SwaraNeural",
     "look": "Northeast Indian girl aged 10, black bob haircut with a straight fringe, bright yellow raincoat, "
             "red rubber boots"},
    {"id": "wanbor", "name": "Wanbor", "role": "authority", "gender": "male", "voice": "hi-IN-MadhurNeural",
     "look": "Northeast Indian man aged 35, short black hair, stubble, black padded jacket, khaki trousers, "
             "holding a long bamboo pole"},
    {"id": "dawan", "name": "Dawan (1988)", "role": "child_boy", "gender": "male", "voice": "hi-IN-MadhurNeural",
     "eleven_settings": {"stability": 0.55, "style": 0.3},
     "look": "Northeast Indian boy aged 9, round face, messy black hair, knitted blue sweater, brown shorts, "
             "a red woollen thread tied on his right wrist"},
    {"id": "dawan_ghost", "name": "Dawan (in the fog)", "role": "child_boy", "gender": "male",
     "voice": "hi-IN-MadhurNeural", "eleven_settings": {"stability": 0.75, "style": 0.1},
     "look": "the same Northeast Indian boy aged 9, round face, messy black hair, knitted blue sweater, brown "
             "shorts, red woollen thread on his right wrist, skin pale grey, dark sad eyes, the edges of his body "
             "fading into fog"},
]

props = [
    {"id": "lantern", "look": "an old brass hurricane lantern with a cracked glass chimney and a faded red woollen "
                              "thread tied to its handle"},
    {"id": "thread_bird", "look": "a small brown-and-yellow bird with a faded red woollen thread tied around one leg"},
    {"id": "basket", "look": "a small round bamboo basket lined with an old checked cloth"},
]

V = "the remote hill village of Jatinga in the Dima Hasao hills of Assam, bamboo-and-tin houses on a green ridge"
FOG = "moonless night, thick drifting blue fog"
T = "an old wooden watchtower on the ridge above Jatinga"
H = "Wanbor's small bamboo house in Jatinga, wooden floor, sacks hung over the windows"
FB = "1988 flashback, warm faded colours"

# (id, setting, characters, mood, props, continuity, [(speaker, hindi, english[, shot])])
scenes = [
    ("s01", f"{T}, {FOG}, a single lantern glowing at the top, hundreds of birds circling it", [], "dread",
     ["lantern"], "the brass lantern glows at the top of the tower", [
        (N, "अगर आप कभी अमावस की रात जतिंगा पहुँचें… तो एक ग़लती मत करना। रोशनी मत जलाना।",
         "If you ever reach Jatinga on a moonless night… never make this one mistake. Don't light a lamp."),
        (N, "पैंतीस साल पहले एक बच्चा उसी रोशनी के पीछे धुंध में गया था… और कभी नहीं लौटा।",
         "Thirty-five years ago a boy followed that light into the fog… and never came back.",
         "a small boy's silhouette walking away into thick blue fog towards a faint glowing light"),
        (N, "असम की दीमा हसाओ पहाड़ियों में एक छोटा सा गाँव है… जतिंगा।",
         "In the Dima Hasao hills of Assam there is a small village… Jatinga."),
        (N, "साल के कुछ ही महीने, अमावस की धुंधली रातों में, यहाँ आसमान से परिंदे गिरते हैं।",
         "For a few months a year, on foggy moonless nights, birds fall from the sky here.",
         "dozens of small birds diving out of thick fog towards a single glowing lantern"),
        (N, "जैसे कोई उन्हें नीचे बुला रहा हो।", "As if someone were calling them down."),
        ("dawan_ghost", "बाबा… रोशनी जलाए रखना… मुझे दिख नहीं रहा।",
         "Baba… keep the light burning… I can't see.",
         "a small pale boy's silhouette standing in thick fog, birds circling above him"),
        (N, "इस गाँव का एक ही नियम है।", "This village has only one rule."),
        (N, "अमावस की रात, सात से दस बजे तक… कोई रोशनी नहीं जलेगी।",
         "On a moonless night, from seven to ten… no light shall burn."),
    ]),
    ("s02", "an old jeep climbing a winding misty mountain road through green Assam hills at dusk", ["meera"], "calm",
     [], "", [
        (N, "उस साल सितंबर में दिल्ली से एक पत्रकार जतिंगा पहुँची। नाम था मीरा।",
         "That September, a journalist from Delhi arrived in Jatinga. Her name was Meera."),
        (N, "उसका काम था ऐसी कहानियों का सच खोलना।", "Her job was to expose stories like this one."),
        ("meera", "परिंदे जो मरने आते हैं? परिंदे खुदकुशी नहीं करते।",
         "Birds that come here to die? Birds don't kill themselves."),
        ("meera", "ये अंधविश्वास है। और मैं इसे साबित करके जाऊँगी।",
         "It's superstition. And I'll prove it before I leave."),
        (N, "जीप ने उसे शाम ढलते गाँव के मोड़ पर उतार दिया।", "The jeep dropped her at the village bend as dusk fell."),
    ]),
    ("s03", f"a muddy lane in {V} at dusk, a man with a bamboo pole and a small girl in a yellow raincoat",
     ["wanbor", "iba", "meera"], "calm", [], "", [
        (N, "गाँव के मोड़ पर उसे वानबोर मिला, हाथ में लंबा बाँस लिए।",
         "At the bend she met Wanbor, holding a long bamboo pole."),
        ("wanbor", "पत्रकार? इस मौसम में? सात बजे से पहले घर के अंदर रहना, मैडम।",
         "A journalist? In this season? Be indoors before seven, madam."),
        ("meera", "क्यों? भूत आता है?", "Why? Does a ghost come?"),
        ("wanbor", "भूत नहीं। परिंदे आते हैं। और जो रोशनी जलाता है, उसी के पास आते हैं।",
         "Not a ghost. The birds come. And they come to whoever lights a lamp."),
        (N, "वानबोर के पीछे से पीले रेनकोट में एक छोटी लड़की झाँकी।",
         "A little girl in a yellow raincoat peeped out from behind Wanbor."),
        ("iba", "बाबा, ये दीदी हमारे घर रुकेंगी?", "Baba, will this didi stay at our house?"),
        ("wanbor", "एक रात। बस एक रात।", "One night. Just one night."),
    ]),
    ("s04", f"inside {H} at dusk, a man blowing out an oil lamp, a girl covering a window with a sack",
     ["wanbor", "iba", "meera"], "dread", [], "", [
        (N, "ठीक सात बजे, पूरे जतिंगा में दीये बुझने लगे।", "At exactly seven, lamps began to go out all over Jatinga.",
         "a row of bamboo houses on a misty ridge going dark one by one"),
        (N, "खिड़कियों पर बोरियाँ टाँग दी गईं। दरवाज़ों की दरारें कपड़ों से भर दी गईं।",
         "Sacks were hung over windows. Cracks in the doors were stuffed with cloth."),
        ("wanbor", "सात से दस। ना दीया, ना टॉर्च, ना मोबाइल की रोशनी। समझीं?",
         "Seven to ten. No lamp, no torch, not even a phone screen. Understood?"),
        ("meera", "और अगर किसी ने जला दी तो?", "And if someone does light one?"),
        (N, "वानबोर चुप रहा।", "Wanbor said nothing."),
        ("iba", "तो वो उसके पास आ जाते हैं।", "Then they come to him."),
    ]),
    ("s05", f"{V} in total darkness, {FOG}, one lantern glowing on top of {T}", ["meera", "wanbor"], "drone",
     ["lantern"], "the brass lantern glows at the top of the tower", [
        (N, "रात के आठ बजे, पूरा गाँव अँधेरे में डूबा था। सिवाय एक जगह के।",
         "By eight, the whole village was drowned in darkness. Except one place."),
        (N, "पहाड़ी पर बने पुराने लकड़ी के टावर पर, एक लालटेन जल रही थी।",
         "On the old wooden tower on the ridge, a lantern was burning.",
         "extreme close-up of an old brass hurricane lantern glowing in fog"),
        ("meera", "वो कौन है?", "Who is that?"),
        ("wanbor", "बा फ्रांग। पैंतीस साल से हर मौसम में वो ये लालटेन जलाता है।",
         "Bah Phrang. For thirty-five years he has lit that lantern every season."),
        ("wanbor", "गाँव वाले उसे कहते हैं… परिंदों को बुलाने वाला।",
         "The villagers call him… the one who calls the birds."),
    ]),
    ("s06", f"birds swirling around the glowing lantern on {T}, {FOG}, a dark tin roof below", ["meera", "wanbor"],
     "pulse", ["lantern"], "the brass lantern glows at the top of the tower", [
        (N, "फिर आवाज़ें शुरू हुईं। पंखों की फड़फड़ाहट। सैकड़ों पंख।",
         "Then the sounds began. The flapping of wings. Hundreds of wings."),
        (N, "धुंध में से परिंदे निकलते और सीधे उस रोशनी की तरफ़ गोता लगाते।",
         "Birds burst out of the fog and dived straight at the light.",
         "a swarm of small dark birds spiralling around a lantern in fog"),
        (N, "मीरा ने कैमरा उठाया।", "Meera raised her camera."),
        ("wanbor", "फ़्लैश मत चलाना! पागल हो क्या?", "Don't use the flash! Are you mad?"),
        (N, "तभी, ठीक उनके सिर के ऊपर, टीन की छत पर कुछ गिरा। धप्प।",
         "Just then, right above their heads, something hit the tin roof. Thud.",
         "a small bird lying still on a wet corrugated tin roof at night"),
    ]),
    ("s07", f"behind {H} on a misty morning, a girl in a yellow raincoat kneeling over a bamboo basket of injured "
            "birds", ["iba", "meera"], "piano", ["basket", "thread_bird"], "", [
        (N, "सुबह मीरा ने इबा को घर के पीछे छुपकर बैठे देखा।",
         "In the morning, Meera found Iba hiding behind the house."),
        (N, "उसकी बाँस की टोकरी में चार-पाँच घायल परिंदे थे।",
         "In her bamboo basket were four or five injured birds.",
         "close-up of a small bamboo basket lined with cloth holding injured little birds"),
        ("iba", "जो बच जाते हैं, उन्हें मैं ठीक करती हूँ। बाबा को मत बताना।",
         "The ones who survive, I heal them. Don't tell Baba."),
        (N, "एक परिंदे के पैर में एक पुराना लाल ऊनी धागा बँधा था।",
         "One bird had an old red woollen thread tied around its leg.",
         "close-up of a small bird's leg with a faded red woollen thread tied around it"),
        ("iba", "ये हर साल आता है। और हर साल इसके पैर में यही लाल धागा होता है।",
         "This one comes every year. And every year it has this same red thread."),
        ("meera", "हर साल? पर इतने साल कोई परिंदा…", "Every year? But no bird lives that many…"),
        (N, "मीरा ने बात अधूरी छोड़ दी।", "Meera left the sentence unfinished."),
    ]),
    ("s08", f"the base of {T} on a foggy morning, an old man polishing a brass lantern", ["phrang", "meera"], "calm",
     ["lantern"], "the lantern is unlit, held in the old man's hands", [
        (N, "उसी दोपहर मीरा टावर पर पहुँची।", "That same afternoon, Meera climbed to the tower."),
        (N, "बा फ्रांग अपनी लालटेन का शीशा साफ़ कर रहे थे।", "Bah Phrang was cleaning the glass of his lantern."),
        ("meera", "आप जानते हैं गाँव वाले आपसे डरते हैं?", "Do you know the villagers are afraid of you?"),
        ("phrang", "डर अच्छा है, बेटी। डर लोगों को घर के अंदर रखता है।",
         "Fear is good, child. Fear keeps people indoors."),
        ("meera", "तो फिर ये लालटेन क्यों? आपकी रोशनी की वजह से परिंदे मरते हैं।",
         "Then why this lantern? Birds die because of your light."),
        ("phrang", "मैं परिंदों के लिए नहीं जलाता।", "I don't light it for the birds."),
        (N, "उन्होंने लालटेन के हत्थे पर बँधे लाल धागे को छुआ।",
         "He touched the red thread tied to the lantern's handle.",
         "close-up of an old wrinkled hand touching a faded red woollen thread on a brass lantern handle"),
        ("phrang", "मैं उसके लिए जलाता हूँ… जो रास्ता भूल गया है।", "I light it for the one… who lost his way."),
    ]),
    ("s09", f"a woman reading old books and printed papers by daylight in {H}", ["meera"], "piano", [], "", [
        (N, "मीरा ने वो सब पढ़ा, जो जतिंगा पर लिखा गया था।", "Meera read everything ever written about Jatinga."),
        (N, "पुराने ज़माने में लोग पहाड़ी पर मशालें जलाते थे, और रोशनी की तरफ़ आए परिंदों को पकड़ लेते थे।",
         "In the old days people lit torches on the ridge and caught the birds that flew to the light."),
        (N, "वैज्ञानिकों ने बरसों इस पर शोध किया। धुंध, तेज़ हवा और रोशनी… यही परिंदों को भटका देते हैं।",
         "Scientists studied it for years. Fog, strong wind and light… that is what confuses the birds."),
        ("meera", "सब कुछ साफ़ है। हवा, धुंध, रोशनी। कोई भूत नहीं।",
         "It's all clear. Wind, fog, light. No ghost."),
        (N, "पर उस रात उसने कुछ ऐसा देखा, जो किसी किताब में नहीं लिखा था।",
         "But that night she saw something no book had written about."),
    ]),
    ("s10", f"the ridge path below {T}, {FOG}, birds swirling around the lit lantern, a woman with a camera crouching",
     ["meera", "dawan_ghost"], "dread", ["lantern"], "the brass lantern glows at the top of the tower", [
        (N, "दूसरी रात, मीरा चुपके से घर से निकली। कैमरा बिना फ़्लैश के।",
         "On the second night, Meera slipped out of the house. Her camera without a flash."),
        (N, "उसने टावर की तरफ़ लंबे एक्सपोज़र की तस्वीरें खींचीं। एक… दो… तीन।",
         "She took long-exposure pictures of the tower. One… two… three.",
         "a woman crouching on a foggy ridge path pointing a camera up at a glowing tower"),
        ("dawan_ghost", "बाबा… और ऊँचा करो… मुझे दिख नहीं रहा।",
         "Baba… hold it higher… I can't see."),
        (N, "मीरा जम गई। आवाज़ उसके ठीक पीछे से आई थी।", "Meera froze. The voice had come from right behind her."),
        (N, "उसने मुड़कर देखा। वहाँ सिर्फ़ धुंध थी।", "She turned around. There was only fog.",
         "empty swirling fog on a dark ridge path, a single bird feather drifting down"),
    ]),
    ("s11", f"inside {H} at night, a woman and a small girl looking at a glowing camera screen under a blanket",
     ["meera", "iba"], "reveal", [], "", [
        (N, "घर लौटकर उसने कंबल के नीचे कैमरे की स्क्रीन देखी।",
         "Back home, she checked the camera screen under a blanket."),
        (N, "तीसरी तस्वीर में, परिंदों के बीच, एक छोटा लड़का खड़ा था।",
         "In the third picture, among the birds, stood a small boy.",
         "a camera screen showing a small boy's silhouette in a blue sweater among birds in fog"),
        (N, "नीला स्वेटर। और कलाई पर लाल धागा।", "A blue sweater. And a red thread on his wrist."),
        ("iba", "ये तो दावान है।", "That's Dawan."),
        ("meera", "कौन दावान?", "Who is Dawan?"),
        ("iba", "बा फ्रांग का बेटा। दादी कहती थीं, वो धुंध में खो गया था। बहुत पहले।",
         "Bah Phrang's son. Grandma used to say he got lost in the fog. A long time ago."),
    ]),
    ("s12", f"the top of {T} on a grey afternoon, an old man looking at a camera screen with trembling hands",
     ["phrang", "meera"], "drone", ["lantern"], "the lantern is unlit, hanging on a nail", [
        (N, "अगले दिन मीरा ने वो तस्वीर बा फ्रांग को दिखाई।", "The next day Meera showed the picture to Bah Phrang."),
        (N, "बूढ़े हाथ काँपने लगे।", "The old hands began to tremble.",
         "close-up of trembling old hands holding a camera"),
        ("phrang", "पैंतीस साल… पैंतीस साल से मैं इसी चेहरे को ढूँढ रहा हूँ।",
         "Thirty-five years… for thirty-five years I have searched for this face."),
        ("meera", "बा फ्रांग, उस रात क्या हुआ था?", "Bah Phrang, what happened that night?"),
    ]),
    ("s13", f"{FB}: a young father tying a red woollen thread on a small boy's wrist on the porch of a bamboo house",
     ["phrang_young", "dawan"], "piano", [], "", [
        (N, "उन्नीस सौ अट्ठासी। दावान नौ साल का था। परिंदों का दीवाना।",
         "Nineteen eighty-eight. Dawan was nine. Crazy about birds."),
        (N, "उस मौसम की पहली रात, फ्रांग ने उसकी कलाई पर एक लाल धागा बाँधा।",
         "On the first night of that season, Phrang tied a red thread on his wrist.",
         "close-up of a man's hands tying a red woollen thread on a small boy's wrist"),
        ("phrang_young", "जब तक ये धागा है, तू कभी नहीं खोएगा।", "As long as you wear this thread, you'll never get lost."),
        ("dawan", "और अगर खो गया तो, बाबा?", "And if I do get lost, Baba?"),
        ("phrang_young", "तो मैं रोशनी जलाऊँगा। तू रोशनी देखकर घर आ जाना।",
         "Then I'll light a lamp. You follow the light and come home."),
    ]),
    ("s14", f"{FB}: men with flaming torches on a foggy ridge at night, birds diving into the fire light, a small boy "
            "running into the fog after a bird", ["dawan", "phrang_young"], "chase", [], "", [
        (N, "उस ज़माने में गाँव वाले रात को पहाड़ी पर मशालें जलाते थे।",
         "In those days, the villagers lit torches on the ridge at night."),
        (N, "दावान चुपके से उनके पीछे गया। उसे बस परिंदों को पास से देखना था।",
         "Dawan sneaked after them. He only wanted to see the birds up close."),
        (N, "एक परिंदा उसके पास गिरा, फिर फड़फड़ाकर धुंध में उड़ गया।",
         "A bird fell near him, then fluttered off into the fog."),
        ("dawan", "रुको! मैं तुम्हें ठीक कर दूँगा!", "Wait! I'll make you better!",
         "a small boy in a blue sweater running into thick fog chasing a fluttering bird"),
        ("phrang_young", "दावान! दावान, वापस आ!", "Dawan! Dawan, come back!"),
        (N, "पूरी रात गाँव ने धुंध छानी। पर दावान कभी नहीं मिला।",
         "The whole village searched the fog all night. But Dawan was never found."),
    ]),
    ("s15", f"the top of {T} on a grey afternoon, an old man and a young woman sitting in silence", ["phrang", "meera"],
     "piano", ["lantern"], "the lantern is unlit, hanging on a nail", [
        ("phrang", "मैंने उससे वादा किया था। रोशनी जलाऊँगा, वो घर आ जाएगा।",
         "I had promised him. I'll light a lamp, and he'll come home."),
        ("phrang", "पैंतीस साल से हर अमावस मैं वही वादा निभा रहा हूँ।",
         "Every moonless night for thirty-five years, I have kept that promise."),
        (N, "मीरा के पास कहने को कुछ नहीं था। उसकी सारी दलीलें चुप हो गई थीं।",
         "Meera had nothing to say. All her arguments had gone quiet."),
        ("meera", "बा फ्रांग… अगर वो सच में वहाँ है… तो वो रोज़ रात किसे बुलाता है?",
         "Bah Phrang… if he really is out there… who is he calling every night?"),
        (N, "बूढ़े ने कोई जवाब नहीं दिया।", "The old man gave no answer."),
    ]),
    ("s16", f"inside {H} at dusk, an angry man with a bamboo pole confronting a young woman, a girl hiding a basket",
     ["wanbor", "meera", "iba"], "drone", ["basket", "thread_bird"], "", [
        ("wanbor", "तुम कहानी लिखकर चली जाओगी। हमें इसी गाँव में रहना है।",
         "You'll write your story and leave. We have to live in this village."),
        ("wanbor", "इबा! आज के बाद उस टावर के पास भी मत जाना।", "Iba! From today, don't even go near that tower."),
        (N, "इबा ने सिर हिलाया। पर उसकी टोकरी पलंग के नीचे छुपी थी।",
         "Iba nodded. But her basket was hidden under the bed."),
        (N, "और उसमें, लाल धागे वाला परिंदा बेचैन फड़फड़ा रहा था।",
         "And inside it, the bird with the red thread was fluttering restlessly.",
         "a small bird with a red thread on its leg fluttering inside a bamboo basket under a bed"),
    ]),
    ("s17", f"the back door of {H} on the darkest night, {FOG}, a small girl in a yellow raincoat stepping into the fog",
     ["iba", "dawan_ghost"], "dread", ["thread_bird"], "", [
        (N, "तीसरी रात अमावस की सबसे गहरी रात थी। धुंध इतनी घनी, कि हाथ को हाथ न सूझे।",
         "The third night was the darkest of the new moon. The fog so thick you couldn't see your own hand."),
        (N, "आधी रात से पहले, लाल धागे वाला परिंदा टोकरी से निकलकर दरवाज़े की दरार से बाहर उड़ गया।",
         "Before midnight, the bird with the red thread slipped out of the basket and flew through a crack in the door."),
        ("iba", "रुको! तुम्हारा पंख अभी ठीक नहीं हुआ!", "Wait! Your wing hasn't healed yet!"),
        (N, "इबा नंगे पाँव उसके पीछे दौड़ी।", "Iba ran after it in her bare feet.",
         "a small girl in a yellow raincoat running barefoot into thick blue fog"),
        ("dawan_ghost", "इबा… इधर आओ… यहाँ बहुत सारे परिंदे हैं।", "Iba… come here… there are so many birds here."),
        (N, "और इबा धुंध में गायब हो गई।", "And Iba vanished into the fog."),
    ]),
    ("s18", f"inside {H} in darkness, a panicked man reaching for a torch, a young woman grabbing his arm",
     ["wanbor", "meera"], "chase", [], "", [
        ("wanbor", "इबा! इबा! कहाँ है मेरी बच्ची?", "Iba! Iba! Where is my child?"),
        (N, "वानबोर ने काँपते हाथों से टॉर्च उठाई। मीरा ने उसका हाथ पकड़ लिया।",
         "Wanbor grabbed a torch with shaking hands. Meera caught his arm."),
        ("meera", "रुकिए! रोशनी मत जलाइए। आपने ही कहा था।", "Stop! Don't switch on a light. You said so yourself."),
        ("wanbor", "मेरी बच्ची बाहर है!", "My child is out there!"),
        ("meera", "मुझे पता है वो कहाँ जा रही है। बा फ्रांग की लालटेन की तरफ़। चलिए!",
         "I know where she's going. Towards Bah Phrang's lantern. Come on!"),
    ]),
    ("s19", f"the top of {T}, {FOG}, an old man holding up a blazing lantern, hundreds of birds swirling",
     ["phrang", "meera", "wanbor"], "pulse", ["lantern"], "the brass lantern blazes in the old man's raised hand", [
        (N, "टावर पर बा फ्रांग अपनी लालटेन ऊँची किए खड़े थे।", "On the tower, Bah Phrang stood holding his lantern high."),
        (N, "उसकी रोशनी के चारों तरफ़ परिंदों का तूफ़ान घूम रहा था।",
         "A storm of birds was whirling around its light.",
         "a storm of birds whirling around a raised brass lantern on a foggy tower"),
        ("phrang", "वो आ रहा है… इस बार वो आ रहा है!", "He's coming… this time he's coming!"),
        ("wanbor", "मेरी बेटी कहाँ है, बूढ़े?", "Where is my daughter, old man?"),
    ]),
    ("s20", f"the edge of the ridge below {T}, {FOG}, a pale boy holding a little girl's hand at the drop, birds "
            "circling", ["dawan_ghost", "iba", "phrang"], "reveal", ["lantern", "thread_bird"],
     "the brass lantern blazes on the tower above them", [
        (N, "धुंध छँटी। पहाड़ी के किनारे, दावान खड़ा था। इबा का हाथ पकड़े।",
         "The fog parted. At the edge of the ridge stood Dawan. Holding Iba's hand.",
         "a pale boy in a blue sweater holding a little girl's hand at the misty edge of a ridge"),
        ("dawan_ghost", "बाबा, देखो… मैं दोस्त लाया हूँ। अब मैं अकेला नहीं रहूँगा।",
         "Baba, look… I've brought a friend. Now I won't be alone."),
        ("phrang", "दावान… मेरे बच्चे…", "Dawan… my child…"),
        ("iba", "बा फ्रांग! ये मुझे नीचे ले जा रहा है!", "Bah Phrang! He's taking me down!"),
        (N, "दावान एक-एक क़दम किनारे की तरफ़ बढ़ रहा था। रोशनी की तरफ़ देखते हुए।",
         "Dawan was moving step by step towards the edge. Looking up at the light."),
    ]),
    ("s21", f"the top of {T}, {FOG}, a young woman shouting at an old man holding a blazing lantern",
     ["meera", "phrang"], "pulse", ["lantern"], "the brass lantern blazes in the old man's hand", [
        ("meera", "बा फ्रांग! लालटेन! वो रास्ता नहीं ढूँढ रहा… वो इसी रोशनी में अटका है!",
         "Bah Phrang! The lantern! He isn't finding his way… he's trapped in this light!"),
        ("meera", "जब तक ये जलती रहेगी, वो यहीं भटकता रहेगा। और किसी न किसी को साथ ले जाएगा।",
         "As long as it burns, he'll keep wandering here. And he'll take someone with him."),
        ("phrang", "अगर मैंने बुझा दी… तो वो घर कैसे आएगा?", "If I put it out… how will he come home?"),
        ("meera", "शायद वो कब का घर जाना चाहता है। आप उसे जाने नहीं दे रहे।",
         "Maybe he wanted to go home long ago. You're not letting him go."),
    ]),
    ("s22", f"the top of {T}, {FOG}, an old man with tears, lips close to the glass of a blazing lantern",
     ["phrang"], "piano", ["lantern"], "the brass lantern is still lit, about to be blown out", [
        (N, "बा फ्रांग ने लालटेन को देखा। पैंतीस साल का वादा।",
         "Bah Phrang looked at the lantern. A promise of thirty-five years."),
        ("phrang", "दावान… मुझे माफ़ कर दे, बेटा। तू खो गया था, और मैं तुझे ढूँढता रह गया।",
         "Dawan… forgive me, son. You were lost, and I never stopped searching."),
        ("phrang", "अब तू जा। अब रोशनी की ज़रूरत नहीं।", "Go now. You don't need the light any more."),
        (N, "और उन्होंने लालटेन बुझा दी।", "And he blew out the lantern.",
         "extreme close-up of an old man blowing out the flame of a brass hurricane lantern"),
    ]),
    ("s23", f"the misty ridge below {T} in darkness, a little girl walking out of the fog holding a small bird, "
            "a man running to hug her", ["iba", "wanbor", "dawan_ghost"], "reveal", ["thread_bird", "lantern"],
     "the lantern on the tower is dark now", [
        (N, "अँधेरा। और फिर एक गहरी ख़ामोशी।", "Darkness. And then a deep silence."),
        (N, "परिंदों का शोर थम गया। वो एक-एक करके पेड़ों पर बैठने लगे।",
         "The noise of the birds stopped. One by one they settled in the trees."),
        (N, "धुंध में से इबा बाहर आई। हाथों में वही लाल धागे वाला परिंदा।",
         "Iba walked out of the fog. In her hands, the same bird with the red thread.",
         "a little girl in a yellow raincoat walking out of fog holding a small bird to her chest"),
        ("wanbor", "इबा! मेरी बच्ची!", "Iba! My child!"),
        ("dawan_ghost", "मैं घर आ गया, बाबा।", "I'm home, Baba.",
         "a faint pale boy's silhouette dissolving into the fog, smiling"),
        (N, "बा फ्रांग ने लालटेन देखी। हत्थे पर बँधा लाल धागा अब वहाँ नहीं था।",
         "Bah Phrang looked at the lantern. The red thread on its handle was gone.",
         "close-up of a dark brass lantern handle with no thread on it"),
    ]),
    ("s24", f"sunrise over {V}, fog lifting, flocks of birds flying away into a golden sky, an old man sitting at "
            f"the foot of {T}", ["phrang", "meera"], "calm", ["lantern"], "the lantern sits unlit beside him", [
        (N, "सुबह जतिंगा पर धूप उतरी। धुंध छँट गई।", "Morning sunlight fell on Jatinga. The fog lifted."),
        (N, "सैकड़ों परिंदे आज़ाद होकर आसमान में उड़ गए।", "Hundreds of birds flew free into the sky.",
         "flocks of birds flying away over green misty hills into a golden sunrise"),
        ("phrang", "पैंतीस साल बाद, आज पहली बार नींद आएगी।", "After thirty-five years, today I'll finally sleep."),
        ("meera", "आपने उसे घर भेज दिया, बा फ्रांग।", "You sent him home, Bah Phrang."),
    ]),
    ("s25", f"a young woman writing at a wooden table by a window in {H}, a camera beside her", ["meera"], "piano",
     [], "", [
        (N, "मीरा ने अपनी रिपोर्ट में वही लिखा, जो विज्ञान कहता है।", "Meera wrote in her report what science says."),
        (N, "धुंध, तेज़ हवा और रोशनी, रात में उड़ते परिंदों को भटका देती है।",
         "Fog, strong wind and light lead night-flying birds astray."),
        (N, "उसने ये भी लिखा, कि जतिंगा के लोग अब परिंदों को पकड़ते नहीं, बचाते हैं।",
         "She also wrote that the people of Jatinga no longer catch the birds. They save them."),
        (N, "पर एक बात उसने रिपोर्ट में नहीं लिखी।", "But one thing she left out of the report."),
        (N, "उसने कैमरे में वो तीसरी तस्वीर फिर देखी। परिंदे थे, धुंध थी… पर लड़का अब वहाँ नहीं था।",
         "She looked at the third picture again. The birds were there, the fog was there… but the boy was gone.",
         "a camera screen showing only birds and fog, no figure"),
    ]),
    ("s26", f"a small window of {H} on a moonless night a year later, {FOG}, a girl in a yellow raincoat at the "
            "window, a small bird landing on the sill", ["iba"], "dread", ["thread_bird"], "", [
        (N, "एक साल बाद। फिर सितंबर। फिर अमावस।", "A year later. September again. A moonless night again."),
        (N, "उस पुराने टावर पर अब कोई लालटेन नहीं जलती।", "No lantern burns on the old tower any more.",
         "an old wooden watchtower standing completely dark in fog"),
        (N, "आधी रात को इबा की खिड़की पर कुछ आकर बैठा।", "At midnight, something landed on Iba's window sill."),
        (N, "एक छोटा सा परिंदा। पैर में लाल धागा।", "A little bird. A red thread on its leg.",
         "a small bird with a red woollen thread on its leg landing on a misty window sill"),
        ("iba", "तुम फिर आ गए?", "You came back?"),
        (N, "और धुंध में कहीं दूर, एक बच्चा हँसा। इस बार… वो आवाज़ डरी हुई नहीं थी।",
         "And somewhere far off in the fog, a child laughed. This time… the voice wasn't afraid."),
    ]),
]

story = {
    "id": "003-jatinga",
    "title": "जहाँ परिंदे मरने आते हैं… 😱 | Jatinga | Hindi Horror Mystery",
    "genre": "horror",
    "art_style": "creepy_comic",
    "language": "hi",
    "logline": "In Jatinga, Assam, where birds dive into lights on moonless nights, a sceptical journalist finds an "
               "old man who has lit a lantern for 35 years for the son he lost in the fog.",
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
        "prompt": "a small pale boy in a blue sweater standing in thick blue fog at the edge of a ridge, hundreds of "
                  "black birds swirling around a single glowing brass lantern held up by an old wrinkled hand",
        "text": "रोशनी मत जलाना",
    },
    "shorts": [
        {"scenes": ["s01"], "title": "यहाँ आसमान से परिंदे गिरते हैं 😱 | Jatinga Horror",
         "hook": "dozens of small birds diving out of thick fog into a single glowing lantern"},
        {"scenes": ["s04", "s05"], "title": "7 बजे के बाद रोशनी जलाई तो… 😱 | Jatinga",
         "hook": "a whole hill village going dark, one lantern glowing on an old tower in the fog"},
        {"scenes": ["s10", "s11"], "title": "इस फ़ोटो में वो बच्चा कौन है? 😱 | Jatinga",
         "hook": "a camera screen showing a small boy's silhouette among birds in fog"},
        {"scenes": ["s21", "s22"], "title": "35 साल से जलती लालटेन बुझानी पड़ी… | Jatinga",
         "hook": "an old man's lips close to a blazing brass lantern, birds circling in fog"},
    ],
    "youtube": {
        "description": "Jatinga, a tiny village in Assam's Dima Hasao hills, is famous for one strange thing: on "
                       "foggy, moonless nights, birds fall out of the sky towards its lights. Meera, a journalist "
                       "from Delhi, comes to prove it is only fog and wind. Then she finds Bah Phrang, an old man "
                       "who has lit a lantern on the ridge every season for 35 years, for the son he lost in the fog.\n\n"
                       "Jatinga and its bird phenomenon are real. The characters and events in this story are fiction.",
        "hashtags": ["#Jatinga", "#AssamHorror"],
        "tags": ["jatinga", "jatinga bird mystery", "jatinga horror story", "assam horror story",
                 "bird suicide village", "northeast india horror", "bhoot ki kahani", "darawani kahani",
                 "horror story in hindi", "hindi horror mystery"],
    },
}

out = ROOT / "queue" / f"{story['id']}.json"
out.write_text(json.dumps(story, indent=2, ensure_ascii=False), encoding="utf-8")
print("wrote", out)
