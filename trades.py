# Sample NSQF-style trade data (MOCK values for prototype; replace with verified NSQF/NCS data)
def t(i,n,hi,kw,cost,m,lo,hi_,home,walk,dem,scheme,nsqf=4,up=None):
    return dict(id=i,name=n,hi=hi,kw=kw,cost=cost,months=m,inc=[lo,hi_],home=home,walk=walk,demand=dem,scheme=scheme,nsqf=nsqf,up=up)
TRADES=[
 t("tailor","Tailoring & Apparel","सिलाई और परिधान",["stitch","tailor","sewing","सिलाई","दर्जी","தையல்"],8000,2,6000,12000,True,True,8,"PM Vishwakarma / PMEGP",4,"embroid"),
 t("embroid","Embroidery & Garment QC","कढ़ाई और गारमेंट क्वालिटी",["embroid","कढ़ाई","எம்பிராய்டரி"],12000,3,9000,16000,True,True,7,"PMKVY / NSFDC loan",5),
 t("mobile","Mobile Phone Repair","मोबाइल रिपेयर",["phone","mobile","repair","मोबाइल","फोन","மொபைல்"],15000,3,10000,20000,False,True,9,"PMKVY / MUDRA",4),
 t("beauty","Beauty & Wellness","ब्यूटी और वेलनेस",["beauty","parlour","parlor","salon","ब्यूटी","पार्लर","அழகு"],12000,3,7000,15000,True,False,7,"PMKVY / Stand-Up India",4),
 t("food","Food Processing & Tiffin","फूड प्रोसेसिंग और टिफिन",["cook","food","tiffin","pickle","खाना","अचार","சமை"],10000,2,6000,14000,True,True,7,"PMFME / SHG credit",3),
 t("data","Data Entry & CSC Operator","डाटा एंट्री और CSC ऑपरेटर",["computer","typing","data entry","कंप्यूटर","कम्प्यूटर","கணினி"],6000,3,8000,15000,True,True,8,"PMKVY / NCS jobs",4),
 t("electric","Electrician (Domestic)","इलेक्ट्रीशियन",["electric","wiring","इलेक्ट्रि","बिजली","மின்"],14000,4,12000,24000,False,False,9,"PMKVY / MUDRA",4),
]

# MOCK anchor buyers - institutional/local demand per trade (replace with verified local survey data)
BUYERS = {
 "tailor": ["3 government schools nearby buying uniforms every June", "Anganwadi centre needs 40 uniform sets yearly", "Local SHG federation outsources stitching orders"],
 "embroid": ["A garment export unit 12 km away hires piece-rate embroiderers", "Wedding-season boutiques in the district town"],
 "mobile": ["Two mobile shops in the block market look for repair help", "Panchayat digital seva kendra needs a repair partner"],
 "beauty": ["Salons in the block town hire on commission", "Wedding season bookings through word of mouth and SHG network"],
 "food": ["Mid-day meal scheme kitchen sources local pickles/snacks", "Weekly haat/mandi stall demand", "SHG-run canteen at the block office"],
 "data": ["Common Service Centre (CSC) needs an operator", "Block office e-governance data entry work"],
 "electric": ["New housing scheme (PMAY) sites need wiring", "Panchayat building maintenance contracts"],
}

# MOCK training provider directory (replace with verified NCVET/SDMS provider data)
PROVIDERS = {
 "tailor": [{"name": "Govt ITI Women's Wing", "score": 82, "km": 6, "seats": 12}, {"name": "SHG Skill Kendra", "score": 74, "km": 3, "seats": 8}],
 "embroid": [{"name": "Apparel Training Centre", "score": 78, "km": 9, "seats": 10}, {"name": "SHG Skill Kendra", "score": 71, "km": 3, "seats": 6}],
 "mobile": [{"name": "PMKVY Electronics Centre", "score": 69, "km": 11, "seats": 15}, {"name": "District Skill Hub", "score": 85, "km": 14, "seats": 10}],
 "beauty": [{"name": "Beauty & Wellness Sector Centre", "score": 76, "km": 8, "seats": 12}, {"name": "SHG Skill Kendra", "score": 65, "km": 3, "seats": 6}],
 "food": [{"name": "PMFME Food Processing Unit", "score": 80, "km": 10, "seats": 20}, {"name": "SHG Skill Kendra", "score": 70, "km": 3, "seats": 8}],
 "data": [{"name": "Common Service Centre Academy", "score": 83, "km": 5, "seats": 15}, {"name": "District Skill Hub", "score": 79, "km": 14, "seats": 10}],
 "electric": [{"name": "Govt ITI", "score": 88, "km": 6, "seats": 12}, {"name": "PMKVY Electrical Centre", "score": 72, "km": 13, "seats": 10}],
}

# Short peer testimonial templates by pathway kind, filled with the trade name
TESTIMONY = {
 "en": {"build": "I already knew {n} from home. PathPal got my skill certified through RPL in weeks, not months. Now I earn from what I always knew.",
        "upgrade": "I used to just do {n} the old way. The upgrade course taught me the parts that pay more. My income went up within a season.",
        "leap": "I never thought I could learn {n}. PathPal listened to what I actually liked, not just my family's work. It changed my path."},
 "hi": {"build": "मुझे {n} पहले से घर पर आता था। PathPal ने RPL से हफ़्तों में मेरा हुनर प्रमाणित करवा दिया, महीनों नहीं लगे। अब मैं अपने जाने-पहचाने काम से कमाती हूँ।",
        "upgrade": "मैं पहले पुराने तरीके से {n} करती थी। अपग्रेड कोर्स ने मुझे ज़्यादा कमाई वाले हिस्से सिखाए। एक सीज़न में ही आय बढ़ गई।",
        "leap": "मैंने कभी नहीं सोचा था कि {n} सीख पाऊँगी। PathPal ने मेरी पसंद सुनी, सिर्फ़ परिवार का काम नहीं। इसने मेरा रास्ता बदल दिया।"},
}
