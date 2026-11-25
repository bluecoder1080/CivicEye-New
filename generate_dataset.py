import random
import csv

categories = ["Pothole", "Garbage", "Streetlight", "Water Leakage", "Drainage", "Other"]
priorities = ["Low", "Medium", "High"]

# Complaint texts grouped by category (varied, realistic, including Hinglish)
complaints_by_category = {
    "Pothole": [
        "Sir main road par ek bada gola hai, gaadiyan gir rahi hain",
        "Merry gully mein paani jama ho raha hai, nali gir pdi hui hai",
        "Nai basti main road t cracked hai, buri tarah from opening",
        "Police station ke peeche dhala gir pda hai, accident risk",
        "Main market main 2-3 feel ghorha hai, gaadiyan uthati hain",
        "College ke gate ke saamne dhala utha hua hai, students fall karte hain",
        "Sector 15 main road main bohot saare golay hain, kabhi sambhala nahi gaya",
        "Mera ghar ke baahar road kharab hai, ghar gari nikalte samay pareshan",
        "Tomar gali main ek bada dhala hai, baarish main paani jama",
        "Buses stand ke point par nali gir hui hai, bus rukte samay mudti hai"
    ],
    "Garbage": [
        "Basti main kachra 3 din se uda nahi, gadbad ho rahi hai",
        "Road par kachra fekne wale milte hain, saamne wale nahi sakte",
        "Nala par kachra jama, gadbad ho rahi hai, smell aa raha",
        "Market complex main garbage bin fill ho gaya, udne ka koi upay nahi",
        "School ke samne road par kachra, bachon padhte samay mudti hai",
        "Park main kachra faela hua hai, safai karne wale nahi aate",
        "Office complex main garbage accumulation, kaam karte waqt pareshan",
        "Residential area main kachra nahi uda, log fekte rehte hain",
        "Festival baad main street completely dirty, safai nahi hui",
        "Paying guest main kachra nikalne ki problematic, landlord nahi sunte"
    ],
    "Streetlight": [
        "Street light gully no 2 mein fail ho gaya, raat main andhera",
        "Main road par 3-4 light lambe samay se buoy gayi hai",
        "College campus main streetlight off hai raat ko, students darte hain",
        "Park main light kharab, raat main dar lagta hai, koi nahi dekhta",
        "Society main streetlight jala nahi raha, bulbs gaya hua",
        "Signal crossing main light blinking, gadiyan rukti hain",
        "Sector main road light engineer ne pakari nahi, 2 mahine se",
        "Gully main 2 mahine se light nahi, raat main ghabrahat hoti",
        "Street light gir pdi, girna ka khatra, baat poochne wale nahi",
        "Tower main light ka voltage kam hai, daba jalta rehta"
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
        "Water tank overflow ho raha, waste, society members pareshan"
    ],
    "Drainage": [
        "Drainage nala overflow ho raha, gadbad, baarish main face nahi kar sakte",
        "Rain main drainage fail, puddle ban gayi, road par jama",
        "Basti main drain choka hua, paani nahi nikal raha, galiboli",
        "School main drainage system kharab, bachon par asar",
        "Office building main drain overflowing, kaam karte waqt problem",
        "Monsoon main drainage main mud aaya, galta hua",
        "Street drain blocked, water jama, garmi main bhapas",
        "Gully main drain smell aa raha hai, beemari ka khatra",
        "Drain cover gir pda, accident risk, bajar main girne wali",
        "River near colony main drainage waste, pollution faayda"
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
        "Public toilet maintenance ka issue, suvidha ka"
    ]
}

# Create balanced dataset: 50 samples per category = 300 total
data = []
for cat in categories:
    selected = random.sample(complaints_by_category[cat], 50)
    for text in selected:
        # Distribute priorities evenly (100 each since 300/3=100)
        pri_idx = len(data) % 3
        pri = priorities[pri_idx]
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