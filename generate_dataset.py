import random
import csv

categories = ["Pothole", "Garbage", "Streetlight", "Water Leakage", "Drainage", "Other"]
priorities = ["Low", "Medium", "High"]

# 50 realistic complaints per category, varied wording, some Hinglish
complaints_by_category = {
    "Pothole": [
        "Sir main road par ek bada gola hai, gaadiyan gir rahi hain",
        "Merry gully mein paani jama ho raha hai, nali gir pdi hui",
        "Nai basti main road t cracked hai, buri tarah se kharaab",
        "Police station ke peeche dhala gir pda hai, accident risk ban gaya",
        "Main market main 2-3 feel ghorha hai, gaadiyan uthati hain",
        "College ke gate ke saamne dhala utha hua hai, students fall karte",
        "Sector 15 main road main bohot saare golay hain, kabhi sambhala nahi gaya",
        "Mera ghar ke baahar road kharab hai, ghar gari nikalte samay pareshan",
        "Tomar gali main ek bada dhala hai, baarish main paani jama rehta",
        "Buses stand ke point par nali gir hui hai, bus rukte samay mudti",
        "Kal se road main ghorha hai, buri tarah se cracked",
        "Kal raat se report kiya, koi action nahi, case pending",
        "Mera issue solve ho gaya, thank you, ab case close",
        "Shayad ye duplicate hai, ignore karo, same wala case",
        "Is tarah ki complaint pehle bhi, same wala topic",
        "Main road se pooja society tak jalan bana hai, 2 saal se",
        "Gadiyan girne ka risk, kabhi bhi ho sakti",
        "Barish main to condition aur buri, paanii jama",
        "Sabse bada gol, sector 12 main, koi nahi nirakshak",
        "Pothole se gaadi ka damage, personal experience",
        "Municipal corporation ko shikayat, sunte nahi",
        "Gali number 3 main 5 baar ghorha, baar baar",
        "School wale bachon ko dikkat, padhte waqt",
        "Pani jama hone par mosquito bane, beemari",
        "Road main ghorha, 2 saal se nahi bharwa",
        "Gol bahut bada, gari nikalte waqt darr lagta",
        "Pothole repairing ka kaam shuru hi nahi",
        "Sarkar waala track, kab milega possible?",
        "Shikayat number par call karo, sunte nahi",
        "Gully main 3 baar girna, adjustment karna pdta",
        "Pothole se students pareshan, exam time",
        "Heavy vehicle se damage, baat poochni",
        "Road condition kharab, election baat bani",
        "Pothole bharwane ka kaam lamba process",
        "Mera road ticketing, pothole wala issue",
        "Gol main puddle, barish main face nahi kar sakte",
        "Road surface kharab, 4-wheeler damage",
        "Pothole wali baat, MLA ko shikayat",
        "Road main girne ka risk, baarish main",
        "Ghara ke samne wala road, tange mein pain"
    ],
    "Garbage": [
        "Basti main kachra 3 din se uda nahi, gadbad ho rahi",
        "Road par kachra fekne wale milte hain, saamne wale nahi",
        "Nala par kachra jama, gadbad ho rahi, smell aa raha",
        "Market complex main garbage bin fill ho gaya, udne ka upay",
        "School ke samne road par kachra, bachon padhte waqt mudti",
        "Park main kachra faela hua, safai karne wale nahi aate",
        "Office complex main garbage accumulation, kaam karte waqt pareshan",
        "Residential area main kachra nahi uda, log fekte rehte",
        "Festival baad main street completely dirty, safai nahi hui",
        "Paying guest main kachra nikalne ki problematic, landlord nahi",
        "Kal se garbage nahi uda, smell aa rahi, baat poochni",
        "Kal raat hi report kiya, koi action nahi aaya",
        "Mera case already pending, dubara shikayat",
        "Koi duplicate complaint, same wala case 2 baar",
        "Garbage wahan fek diya, wahan se begin",
        "Nagar nigam wala baar baar nahi aata",
        "Kachra udne wale log, kahaan se la kar jaate",
        "3 din se uda nahi, smell se beetar ho raha",
        "Park wale area main, bachon khelne ka injury",
        "Kachra gale mein, beemari ka reason ban sakta",
        "Festival baad main kachra, 1 week lagta saaf hona",
        "Paying guest main kachra, landlord baat nahi sakte",
        "Office main kachra, kaam karte waqt pareshan",
        "Society main kachra collection, Sunday ko baat",
        "Ghar main kachra management, daily routine",
        "Market wale plastic bag, gaaiyaan pareshan",
        "Bio-degradable waste, set up karna chahiye",
        "Kachra burning wala, pollution bana rakha",
        "Domestic waste collection, time pe nahi aata",
        "Flat wale area main, kachra nahi ud pa raha",
        "Street vendor waste, rasta rok raha",
        "Household kachra, 2 baar collection hui",
        "Area wale safai karamchari, 1 mahine se nahi aaye"
    ],
    "Streetlight": [
        "Street light gully no 2 mein fail ho gaya, raat main andhera",
        "Main road par 3-4 light lambe samay se buoy gayi",
        "College campus main streetlight off hai raat ko, students darte",
        "Park main light kharab, raat main dar lagta, koi nahi dekhta",
        "Society main streetlight jala nahi raha, bulbs gaya hua",
        "Signal crossing main light blinking, gadiyan rukti hain",
        "Sector main road light engineer ne pakari nahi, 2 mahine se",
        "Gully main 2 mahine se light nahi, raat main ghabrahat hoti",
        "Street light gir pdi, girna ka khatra, baat poochne wale nahi",
        "Tower main light ka voltage kam hai, daba jalta rehta",
        "Kal se light off, tension hai, power department se shikayat",
        "Kal raat hi galti se off, dobara start nahi hui",
        "Light dim hai, kabhi kabhi off, electrician call karna",
        "Main road light fail, raat main dar lagta, koi nahi jaga",
        "Gully main light na hon par, raat main galti hoti",
        "Streetlight off hone par, women feel unsafe",
        "High mast light gir pdi, bada accident risk",
        "Electricity bill badh raha, light kam jal rahi",
        "Gully main akeli andar ja sakti, dark mein",
        "Light repaired hone mein 2 mahine lag gaye",
        "Streetlight shuru hone se, ghaltiyan kam hui",
        "Gully main dark raha, raat ko galti hoti",
        "Pole light gir pdi, adjustment karna padega",
        "Electric wire niche gir pdi, baat poochni",
        "Light main fuse, baar baar ghaltiyan",
        "Streetlight main remote, kabhi kabhi fail",
        "Gully main akeli baat, dark mein dar lagta",
        "High mast maintenance, 6 mahine se pending",
        "Light beam kharab, raat main farak nahi padega",
        "Street light off hone par, ghaltiyan beet jati",
        "Electricity cutoff wala notice, kab milega?",
        "Streetlight repair wala, dobara shuru nahi hua"
    ],
    "Water Leakage": [
        "Ghar main paani gir raha, waste water, billing badh gayi",
        "Main pipe burst ho gayi, water multi road par, traffic rokdi",
        "Billi ki nali se paani tut raha hai, bill dena banda",
        "Bathroom ka tap fail ho gaya, bohot paani waste, bill badh raha",
        "Garden main irrigation pipe burst, pani barbaad ho raha",
        "Terrace main water leakage se ceiling gir raha, maal bachaya",
        "Cooling system main water leak, AC adjust karna par",
        "Pipe connection loose, water flowing on road, jams",
        "Fridge se paani tut raha supply line main, khana kharab",
        "Water tank overflow ho raha, waste, society members pareshan",
        "Kal se water supply ruka, tension hai, koi nahi sun raha",
        "Kal raat hi overflow hua, suvidha chali gayi",
        "Mera case already pending, dubara shikayat",
        "Water billing bahut badh gayi, galat reading hui",
        "Ghar main dripping sunne ko, ratebaaz bhav",
        "Pipe fitti main leak, baarish mein badh jaye",
        "Upper floor main leak, niche wale ko dikkat",
        "Socity main water tank overflow, beetar baat",
        "Pipe wala kharab, sirf temporary fix",
        "Basement main water, beetar baat ban gayi",
        "Ceiling main stain, water leakage wala scar",
        "Wall main damp, painting gir rahi",
        "Bathroom main water, every samay baat",
        "Kitchen sink leak, daily usage problem",
        "Water meter kharab, reading galat aati",
        "Society main tank, cleaning baaki rehti",
        "Pipe connection change, 3 baar ho chuka",
        "Water pressure kam, ghaltiyan hoti",
        "Leakage point nahi dikh raha, dhundne wala",
        "Pipe fitti main crack, water jama",
        "Socity main pipe burst, 2 ghante tak",
        "Upper floor main leak, niche wale pareshan",
        "Water bill double hui, reason poochna",
        "Leakage repair wala, 2 mahine se",
        "Pipe wala kharab, two baar fix hua"
    ],
    "Drainage": [
        "Drainage nala overflow ho raha, gadbad, baarish main face nahi",
        "Rain main drainage fail, puddle ban gayi, road par jama",
        "Basti main drain choka hua, paani nahi nikal raha, galiboli",
        "School main drainage system kharab, bachon par asar",
        "Office building main drain overflowing, kaam karte waqt problem",
        "Monsoon main drainage main mud aaya, galta hua",
        "Street drain blocked, water jama, garmi main bhapas",
        "Gully main drain smell aa raha, beemari ka khatra",
        "Drain cover gir pda, accident risk, bajar main girne wali",
        "River near colony main drainage waste, pollution faayda",
        "Kal se drain choka, paani nahi nikal raha, case pending",
        "Kal raathi backup bana, kal main kharcha",
        "Mera case already processed, dubara status",
        "Same wala problem, different location pe dikhwa",
        "Drain overflow hone par, gali main baarish",
        "Nala choka hone par, 2 gadiyan gir gayi",
        "Water nikalne wala machine kharab",
        "Drain saaf karna, 1 saal se nahi hua",
        "Gully main paani jama, beetar baat ban gayi",
        "Drain block wala, chemical dhundne wala",
        "Drain cover girna, adjustment karna padega",
        "Gully main water, beetar baat shuru",
        "Sewage smell, health risk baat poochni",
        "Drain line blocked, 2 baar clear karwa",
        "Rain water main, raat main face nahi kar sakte",
        "Drain maintenance wala, baar baar baat",
        "Gully main stagnant water, beemari wala khatra",
        "Drain cover missing, baat poochni",
        "Drain blockage wala, chemical treatment",
        "Rain water main, road par jama rehta",
        "Drain overflow wala, gali main mud",
        "Gully main water jama, beetar baat",
        "Sewage treatment plant, kaam karna chahiye"
    ],
    "Other": [
        "Electric wire gir pdi main road par, accident risk",
        "Tree gir pdi, road block hai, raste badal gaye",
        "Dog biting people main park main, baat karne wale darte",
        "Noise pollution shuru, construction work, suvarna samay",
        "Main road par traffic jam permanent, office jaanewaale",
        "Koi accident scene clear nahi hua, police nahi aa rahi",
        "WiFi signal kam ho gaya, tech issue, office kaam nahi",
        "Light main remote kaam nahi kar raha, naya lena parega",
        "Society main gate lock kharab, ghar aane jane ka",
        "Public toilet maintenance ka issue, suvidha ka",
        "Kal se priority change karni thi, case pending",
        "Kal main dekhunga case, kal raat follow up",
        "Mera issue solve ho gaya, thank you, ab close",
        "Serial complaint karta rehunga, har baar naya",
        "Electricity bill badh gayi, service kharab",
        "Water connection dene ka anmolan, lamba process",
        "Society main park main, boring kharab",
        "Street main painting ka kaam, 6 mahine se",
        "Koi badda sawal, officer se poochna",
        "WiFi password badalna, tech support chahiye",
        "Light main switch, kharab ho raha",
        "Society main park, swing gir pdi hui",
        "Street main digging, 3 mahine se chal raha",
        "Koi parv, setting shuru, jagah nahi mili",
        "Park main grass, gardener nahi aaya",
        "Public toilet, cleaning baaki reh gayi",
        "Street light main, remote control kharab",
        "Society main gate, auto close nahi ho raha",
        "Park main bench, टूटी हुयी हालत",
        "Public facility, maintenance ka kaam",
        "Electric pole main, wire gir pdi hui",
        "Koi sawal, related tech support",
        "WiFi range badhwana, signal kam hai",
        "Light main board, display kharab hua",
        "Society main park, plants suit nahi",
        "Street main banner, ugal pda hua",
        "Public property, damage ka case pending",
        "Electric fitting, spark wali baat poochni",
        "Koi pareshani, batana zaruri"
    ]
}

# Create balanced dataset: 50 samples per category = 300 total
# Distribute priorities evenly: 100 Low, 100 Medium, 100 High
data = []
pri_cycle = iter(priorities * 100)  # cycle through Low x100, Medium x100, High x100

for cat in categories:
    selected = random.sample(complaints_by_category[cat], 50)
    for text in selected:
        pri = next(pri_cycle)  # get next priority in cycle
        data.append((text, cat, pri))

# Shuffle the data
random.shuffle(data)

# Write to CSV
with open('dataset.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(['text', 'category', 'priority'])
    for text, cat, pri in data:
        writer.writerow([text, cat, pri])

print(f"Created dataset with {len(data)} rows")

print(f"\nCategory distribution:")
cat_counts = {}
for text, cat, pri in data:
    cat_counts[cat] = cat_counts.get(cat, 0) + 1
for cat, count in sorted(cat_counts.items()):
    print(f"  {cat}: {count}")

print(f"\nPriority distribution:")
pri_counts = {}
for text, cat, pri in data:
    pri_counts[pri] = pri_counts.get(pri, 0) + 1
for pri, count in sorted(pri_counts.items()):
    print(f"  {pri}: {count}")