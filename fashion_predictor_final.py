"""
StyleIQ — Enhanced Fashion Predictor ML Model
RandomForest + Occasion Engine + Wardrobe Generator
IBM Internship Project
"""
import numpy as np
from sklearn.ensemble import RandomForestClassifier
import random

class FashionPredictor:
    STYLES  = ["Minimalist","Streetwear","Casual Chic","Athletic","Formal","Bohemian","Elegant"]
    SIZES   = ["XS","S","M","L","XL","XXL"]

    STYLE_MAP = {
        ("male",  "slim"):     ["Minimalist","Streetwear","Formal"],
        ("male",  "athletic"): ["Athletic","Streetwear","Casual Chic"],
        ("male",  "average"):  ["Casual Chic","Minimalist","Streetwear"],
        ("male",  "muscular"): ["Athletic","Streetwear","Casual Chic"],
        ("male",  "heavy"):    ["Casual Chic","Streetwear","Formal"],
        ("female","slim"):     ["Minimalist","Elegant","Bohemian"],
        ("female","athletic"): ["Athletic","Casual Chic","Streetwear"],
        ("female","average"):  ["Casual Chic","Elegant","Minimalist"],
        ("female","hourglass"):["Elegant","Formal","Bohemian"],
        ("female","petite"):   ["Minimalist","Casual Chic","Bohemian"],
        ("female","curvy"):    ["Bohemian","Elegant","Casual Chic"],
        ("other", "slim"):     ["Minimalist","Streetwear","Bohemian"],
        ("other", "athletic"): ["Athletic","Streetwear","Casual Chic"],
        ("other", "average"):  ["Streetwear","Minimalist","Casual Chic"],
    }

    OCCASION_OUTFITS = {
        "work":       {
            "male":   ["Navy blazer + white shirt + grey chinos + Oxford shoes","Charcoal suit + light blue shirt + leather belt","Slim trousers + turtleneck + Chelsea boots"],
            "female": ["Tailored blazer + silk blouse + pencil skirt + heels","Smart trousers + structured top + loafers","Midi wrap dress + blazer + block heels"],
        },
        "casual":     {
            "male":   ["Quality tee + slim denim + white sneakers","Linen shirt + shorts + espadrilles","Polo shirt + chinos + loafers"],
            "female": ["Mom jeans + tucked tee + mule sandals","Flowy midi skirt + fitted tank + trainers","Denim jacket + sundress + sneakers"],
        },
        "formal":     {
            "male":   ["Three-piece navy suit + white shirt + silk tie","Charcoal tuxedo + bow tie + patent shoes","Black suit + French-cuff shirt + cufflinks"],
            "female": ["Floor-length gown + strappy heels + clutch","Tailored jumpsuit + heels + statement earrings","Silk wrap dress + block heels + pearl jewellery"],
        },
        "evening":    {
            "male":   ["Black turtleneck + tailored trousers + Chelsea boots","Dark blazer + tee + slim jeans + loafers","Velvet blazer + white shirt + dark trousers"],
            "female": ["Satin slip dress + mule heels + mini bag","Velvet wrap dress + ankle boots + hoop earrings","Sequin top + wide-leg trousers + strappy heels"],
        },
        "weekend":    {
            "male":   ["Oversized hoodie + joggers + chunky sneakers","Linen co-ord set + sandals","Graphic tee + cargo shorts + trainers"],
            "female": ["Oversized sweater + leggings + trainers","Linen jumpsuit + sandals + straw bag","Crop top + wide-leg jeans + platform sneakers"],
        },
        "smart_casual":{
            "male":   ["Blazer + tee + dark jeans + Chelsea boots","Knit polo + chinos + loafers","Shirt jacket + turtleneck + slim trousers"],
            "female": ["Knit dress + ankle boots + tote bag","Tailored shorts + blouse + block heels","Shirt dress + belt + white trainers"],
        },
        "gym":        {
            "male":   ["Compression shorts + performance tee + running shoes","Joggers + dry-fit top + training shoes","Shorts + sleeveless tank + cross-trainers"],
            "female": ["High-waist leggings + sports bra + mesh jacket","Seamless set + trainers","Cycling shorts + longline sports bra + sneakers"],
        },
        "beach":      {
            "male":   ["Board shorts + linen shirt + flip flops","Swim shorts + muscle tee + sandals","Linen co-ord + espadrilles + sunhat"],
            "female": ["Bikini + sarong + espadrilles + wide-brim hat","Swimsuit + crochet cover-up + sandals","High-waist bikini + linen shorts + slides"],
        },
        "wedding":    {
            "male":   ["Morning suit + waistcoat + top hat","Navy suit + floral tie + pocket square","Grey three-piece + white shirt + Oxford shoes"],
            "female": ["Floral midi dress + block heels + fascinator","Pastel gown + strappy sandals + clutch","Lace wrap dress + kitten heels + pearl jewellery"],
        },
        "date":       {
            "male":   ["Dark slim jeans + fitted shirt + Chelsea boots","Smart chinos + linen shirt + loafers","Black jeans + roll-neck + clean trainers"],
            "female": ["Wrap dress + heels + small handbag","High-waist trousers + crop top + mules","Mini skirt + oversized blazer + ankle boots"],
        },
    }

    WEEK_OUTFITS = {
        "Minimalist": {
            "male":   ["White tee + grey chinos + white sneakers","Linen shirt + slim trousers + loafers","Grey rollneck + dark jeans + Chelsea boots",
                       "Navy suit + white tee + Oxford shoes","Clean white tee + black jeans + minimalist trainers","Oversized linen shirt + linen shorts + sandals","Relaxed trousers + tucked tee + slip-ons"],
            "female": ["Slip dress + loafers + minimal jewellery","Wide-leg trousers + fitted tank + sandals","Oversized blazer + bike shorts + ankle boots",
                       "Tailored co-ord set + pointed heels","Relaxed midi dress + trainers + tote","Linen co-ord + espadrilles","Simple sundress + sandals + sun hat"],
        },
        "Elegant":    {
            "male":   ["Navy blazer + turtleneck + tailored trousers","Charcoal suit + silk pocket square","Black roll-neck + slim trousers + Chelsea boots",
                       "Three-piece suit + white shirt","Smart velvet blazer + dark trousers","Cashmere V-neck + slim chinos + loafers","Relaxed linen suit + espadrilles"],
            "female": ["Silk blouse + wide-leg trousers + heels","Velvet midi dress + block heels","Tailored blazer + satin skirt + pumps",
                       "Wrap dress + kitten heels + pearl earrings","Shift dress + structured bag + loafers","Flowy maxi + strappy sandals","Silk slip + blazer + ankle boots"],
        },
        "Streetwear": {
            "male":   ["Graphic tee + cargo pants + chunky sneakers","Hoodie + joggers + Air Force 1s","Bomber jacket + straight denim + Jordans",
                       "Vintage tee + wide-leg trousers + platform sneakers","Puffer vest + long-sleeve + cargos","Co-ord tracksuit + high-tops","Oversized shirt + biker shorts + chunky trainers"],
            "female": ["Crop hoodie + biker shorts + platform trainers","Oversized tee + baggy jeans + retro sneakers","Tracksuit set + chunky trainers + crossbody",
                       "Corset top + wide-leg jeans + air max","Crop jacket + cargo trousers + boots","Mini skirt + graphic tee + chunky sneakers","Streetwear co-ord + snapback + trainers"],
        },
        "Casual Chic":  {
            "male":   ["Polo tee + chinos + loafers","Linen shirt + shorts + espadrilles","Smart tee + slim denim + white sneakers",
                       "Knit jumper + slim trousers + Chelsea boots","Button-down + jogger chinos + trainers","Striped tee + navy shorts + sandals","Camp-collar shirt + linen shorts + flip-flops"],
            "female": ["Floral midi skirt + fitted top + sandals","Straight jeans + linen blouse + mules","Smock dress + trainers + bucket hat",
                       "Tailored shorts + knit top + loafers","Wrap top + wide-leg jeans + block heels","Shirt dress + belt + sneakers","Ruched dress + espadrilles + woven bag"],
        },
        "Athletic":   {
            "male":   ["Performance tee + compression shorts + running shoes","Joggers + hoodie + training shoes","Shorts + sleeveless tee + cross-trainers",
                       "Track jacket + joggers + sneakers","Dry-fit polo + chinos + clean trainers","Gym shorts + muscle tank + slides","Athletic co-ord + running shoes"],
            "female": ["Leggings + sports bra + zip-up jacket","Seamless gym set + trainers","Cycling shorts + crop tee + sneakers",
                       "Athletic dress + trainers","Yoga pants + longline bra + hoodie","Running set + cap + trainers","Shorts + racerback top + slides"],
        },
        "Formal":     {
            "male":   ["Navy suit + white shirt + silk tie + Oxford shoes","Charcoal blazer + dress shirt + trousers","Black tuxedo + bow tie + patent shoes",
                       "Grey suit + patterned tie + leather shoes","Navy blazer + chinos + loafers","Three-piece suit + white pocket square","Dark suit + French cuff shirt + cufflinks"],
            "female": ["Tailored pantsuit + silk blouse + heels","Midi sheath dress + structured bag + heels","Blazer dress + court shoes",
                       "A-line skirt + blouse + heels","Smart jumpsuit + heels + earrings","Shift dress + blazer + loafers","Floor-length gown + strappy heels"],
        },
        "Bohemian":   {
            "male":   ["Linen shirt + flared trousers + leather sandals","Embroidered shirt + wide-leg pants + woven belt","Breezy co-ord + espadrilles",
                       "Printed shirt + linen shorts + sandals","Peasant top + relaxed chinos + sandals","Flowing linen set + leather sandals","Printed linen + wide-leg trousers + slip-ons"],
            "female": ["Floral maxi + platform sandals + layered jewellery","Peasant blouse + wide-leg pants + sandals","Crochet top + denim skirt + ankle boots",
                       "Wrap maxi + strappy sandals + bangles","Off-shoulder dress + espadrilles + woven bag","Tiered skirt + linen top + sandals","Prairie dress + ankle boots + belt bag"],
        },
    }

    def __init__(self):
        self.model = self._train()

    def _train(self):
        np.random.seed(42)
        n = 2000
        heights = np.random.normal(170, 12, n)
        weights = np.random.normal(68, 15, n)
        ages    = np.random.randint(16, 65, n)
        bmis    = weights / ((heights / 100) ** 2)
        sizes   = [0 if b<17.5 else 1 if b<20 else 2 if b<23 else 3 if b<27 else 4 if b<32 else 5 for b in bmis]
        model   = RandomForestClassifier(n_estimators=120, random_state=42, max_depth=9, n_jobs=-1)
        model.fit(np.column_stack([heights, weights, ages, bmis]), sizes)
        return model

    def predict(self, height, weight, age, gender, body_type):
        bmi     = weight / ((height / 100) ** 2)
        X       = np.array([[height, weight, age, bmi]])
        sz_idx  = self.model.predict(X)[0]
        sz_prob = self.model.predict_proba(X)[0]

        key      = (gender.lower(), body_type.lower())
        fallback = (gender.lower(), "average")
        choices  = self.STYLE_MAP.get(key, self.STYLE_MAP.get(fallback, ["Casual Chic","Minimalist"]))

        age_bonus = ["Streetwear","Athletic"] if age<25 else ["Casual Chic","Minimalist"] if age<40 else ["Formal","Elegant","Minimalist"]
        combined  = choices + [s for s in age_bonus if s in self.STYLES]
        style     = combined[0]
        alts      = list(dict.fromkeys(combined[1:]))[:3]

        bmi_ok   = 16 <= bmi <= 35
        conf     = min(97, 78 + (10 if bmi_ok else 0) + (5 if key in self.STYLE_MAP else 0) + random.randint(-3, 5))
        sz_conf  = round(float(np.max(sz_prob)) * 100, 1)

        return {
            "style": style, "alt_styles": alts,
            "size":  self.SIZES[sz_idx], "bmi": round(bmi,1),
            "bmi_category": self._bmi_cat(bmi),
            "confidence": conf, "size_confidence": sz_conf,
            "outfits":       self._outfits(style, gender),
            "color_palette": self._palette(style),
            "season_tip":    self._tip(style),
        }

    def occasion_predict(self, style, gender, occasion):
        g    = gender.lower() if gender.lower() in ["male","female"] else "male"
        opts = self.OCCASION_OUTFITS.get(occasion, self.OCCASION_OUTFITS["casual"])
        return opts.get(g, opts.get("male", ["Smart casual outfit"]))

    def generate_week_outfits(self, style, gender, schedule, size):
        g = gender.lower() if gender.lower() in ["male","female"] else "male"
        week = self.WEEK_OUTFITS.get(style, self.WEEK_OUTFITS["Casual Chic"])
        pool = week.get(g, week.get("male", [""]*7))
        # Blend with occasion-specific items
        result = []
        for occ in schedule:
            occ_outfits = self.OCCASION_OUTFITS.get(occ, {}).get(g, [])
            if occ_outfits and random.random() > 0.4:
                result.append(random.choice(occ_outfits))
            else:
                result.append(pool[len(result) % len(pool)])
        return result[:7]

    def _outfits(self, style, gender):
        db = {
            "Minimalist": {"male":["White Oxford + slim chinos + white sneakers","Monochrome tonal set in grey or beige","Structured overcoat + turtleneck + tapered trousers"],
                           "female":["Slip dress + loafers + minimal gold jewellery","Wide-leg linen pants + fitted tank + sandals","Oversized blazer + bike shorts + ankle boots"]},
            "Streetwear": {"male":["Graphic tee + cargo pants + chunky sneakers","Hoodie + joggers + high-top Air Force 1s","Bomber jacket + straight-leg denim + Jordans"],
                           "female":["Oversized hoodie + biker shorts + platform sneakers","Crop top + baggy jeans + retro sneakers","Tracksuit set + chunky trainers + crossbody bag"]},
            "Casual Chic":{"male":["Quality tee + slim denim + leather loafers","Polo shirt + chinos + suede Chelsea boots","Linen shirt + shorts + clean white sneakers"],
                           "female":["Flowy midi skirt + fitted top + strappy sandals","Mom jeans + tucked blouse + mule heels","Wrap dress + espadrilles + sun hat"]},
            "Athletic":   {"male":["Compression shorts + performance tee + running shoes","Jogger pants + zip-up hoodie + training shoes","Shorts + sleeveless tee + high-top sneakers"],
                           "female":["High-waist leggings + sports bra + mesh jacket","Training shorts + racerback tank + running shoes","Yoga pants + long-sleeve crop + sneakers"]},
            "Formal":     {"male":["Navy suit + white shirt + silk tie + Oxford shoes","Charcoal blazer + dress trousers + pocket square","Three-piece suit + French cuff shirt + cufflinks"],
                           "female":["Tailored pantsuit + silk blouse + pointed heels","Pencil skirt + structured blazer + pumps","Wrap dress + blazer + strappy heels"]},
            "Elegant":    {"male":["Black turtleneck + tailored trousers + Chelsea boots","Cashmere V-neck + slim trousers + loafers"],
                           "female":["Satin slip dress + strappy heels + clutch","Velvet wrap dress + block heels + pearl earrings","Maxi gown + statement earrings + stilettos"]},
            "Bohemian":   {"male":["Linen shirt + flared trousers + leather sandals","Embroidered shirt + wide-leg pants + woven belt"],
                           "female":["Floral maxi dress + platform sandals + layered jewellery","Peasant blouse + wide-leg pants + leather sandals","Crochet top + denim skirt + ankle boots + hat"]},
        }
        g = gender.lower() if gender.lower() in ["male","female"] else "male"
        return (db.get(style,{}).get(g, ["Smart casual look + clean sneakers"]))[:3]

    def _bmi_cat(self, bmi):
        if bmi<18.5: return "Underweight"
        if bmi<25:   return "Normal weight"
        if bmi<30:   return "Overweight"
        return "Obese"

    def _palette(self, style):
        return {
            "Minimalist":  ["#FFFFFF","#000000","#F5F0EB","#C4C4C4","#2C2C2C"],
            "Streetwear":  ["#1A1A1A","#FF4500","#00E5FF","#F5F5F5","#8B00FF"],
            "Casual Chic": ["#F4E4C1","#8B6914","#4A7C59","#2C4A7C","#E8C4A0"],
            "Athletic":    ["#0055FF","#FF2200","#00FF88","#1A1A1A","#FFFFFF"],
            "Formal":      ["#1C2951","#2C3E50","#8E9EAB","#BDC3C7","#F8F9FA"],
            "Bohemian":    ["#C8A96E","#8B4513","#556B2F","#9370DB","#D2691E"],
            "Elegant":     ["#1C1C1E","#2C1810","#4A0E4E","#C0A882","#F5E6D3"],
        }.get(style, ["#000000","#FFFFFF","#888888"])

    def _tip(self, style):
        return {
            "Minimalist":  "Invest in 3 quality basics: white tee, dark denim, camel coat. These 3 items alone create 27+ outfit combinations.",
            "Streetwear":  "Build around one statement shoe or jacket. Everything else should support it, not compete.",
            "Casual Chic": "The difference between 'casual' and 'casual chic' is one quality piece — a linen blazer or leather sandals.",
            "Athletic":    "Tonal monochrome sets (all-black, all-grey) always look more intentional at the gym and beyond.",
            "Formal":      "Fit over brand, always. A $100 suit that fits perfectly outperforms a $1000 suit that doesn't.",
            "Bohemian":    "Layer thoughtfully: linen, crochet, leather. The beauty is in texture contrast, not colour matching.",
            "Elegant":     "Restraint is luxury. One statement piece, impeccable grooming, and quality fabric does all the work.",
        }.get(style, "Style is confidence made visible — wear what makes you feel powerful.")
