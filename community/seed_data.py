import logging
from django.utils import timezone
from .models import CommunityPost, CommunityAnswer

logger = logging.getLogger(__name__)

INITIAL_POSTS = [
    {
        "author_name": "Amol Ganganmale",
        "author_location": "India",
        "crop": "Capsicum & Chilli",
        "crop_icon": "🌶️",
        "title": "Help identifying problem with my Chilli",
        "description": "Plantix has detected a possible problem with my Capsicum & Chilli. I was given a few possibilities: ‼️ #Helicoverpa Caterpillar, ‼️ #Sunburn or ‼️ #Healthy. Can you help me identifying the issue?",
        "image_url": "/static/images/community/chilli-problem.jpg",
        "tags": "#Helicoverpa Caterpillar, #Sunburn, #Healthy",
        "likes": 14,
        "dislikes": 0,
        "answers": [
            {
                "author_name": "Dr. S. K. Patil",
                "author_role": "KVK Agronomist • Maharashtra",
                "content": "This is primarily Sunburn combined with early thrips feeding. Provide partial shade during high heat index, avoid excessive pruning of the protective canopy, and spray Neem seed kernel extract (NSKE 5%) or Imidacloprid 17.8 SL (0.3 ml/L) if thrips count exceeds 5 per leaf.",
                "likes": 9,
                "is_verified": True,
            }
        ]
    },
    {
        "author_name": "Vinod Kumar Vinod K...",
        "author_location": "India",
        "crop": "Tomato",
        "crop_icon": "🍅",
        "title": "Help identifying problem with my Tomato",
        "description": "Plantix has detected a possible problem with my Tomato. I was given a few possibilities: ‼️ #Early Blight, ‼️ #Septoria or ‼️ #Healthy. Lower leaves are turning yellow with brown target-like concentric rings.",
        "image_url": "/static/images/pests/early-blight.jpg",
        "tags": "#Early Blight, #Septoria, #Healthy",
        "likes": 11,
        "dislikes": 0,
        "answers": [
            {
                "author_name": "Rameshwar Patel",
                "author_role": "Experienced Tomato Grower • Gujarat",
                "content": "This is textbook Early Blight (Alternaria solani). Immediately remove and destroy affected lower foliage touching wet soil. Switch from sprinkler to drip irrigation so leaves stay dry.",
                "likes": 5,
                "is_verified": False,
            },
            {
                "author_name": "Dr. Meenakshi Sundaram",
                "author_role": "Plant Pathologist • TNAU",
                "content": "Spray Mancozeb 75 WP @ 2.5 g/L or Azoxystrobin 23 SC @ 1 ml/L. Ensure full coverage on the undersides of the leaves. Maintain proper crop rotation with non-solanaceous crops.",
                "likes": 12,
                "is_verified": True,
            }
        ]
    },
    {
        "author_name": "Pooja Patil",
        "author_location": "Maharashtra",
        "crop": "Pumpkin",
        "crop_icon": "🎃",
        "title": "Powdery white patches spreading on pumpkin leaves",
        "description": "White powdery fungal patches are spreading very fast on leaves and stems following high humidity. Need an effective biological or organic control method before fruiting.",
        "image_url": "/static/images/pests/mosaic.jpg",
        "tags": "#Powdery Mildew, #Organic Control, #Cucurbits",
        "likes": 8,
        "dislikes": 0,
        "answers": [
            {
                "author_name": "Kailash Jadhav",
                "author_role": "Organic Farmer • Nashik",
                "content": "Mix 100 ml raw cow milk with 900 ml clean water and 2 ml liquid soap as a sticker. Spray early in the morning under bright sunlight. The lactoferrin proteins generate free radicals under UV that eliminate mildew colonies naturally.",
                "likes": 7,
                "is_verified": True,
            }
        ]
    },
    {
        "author_name": "Suresh Reddy",
        "author_location": "Andhra Pradesh",
        "crop": "Rice",
        "crop_icon": "🌾",
        "title": "Yellowing leaf tips in Paddy crop (30 DAT)",
        "description": "My paddy nursery transplant is 30 days old. Tips of older leaves are showing marginal scorching and yellowing. Is this Potassium deficiency or Bacterial Leaf Blight?",
        "image_url": "/static/images/pests/rice-blight.jpg",
        "tags": "#Paddy, #Bacterial Blight, #Potash",
        "likes": 21,
        "dislikes": 1,
        "answers": [
            {
                "author_name": "M. Venkateswara Rao",
                "author_role": "Rice Specialist • ANGRAU",
                "content": "Examine the leaf margins carefully. If dry with wavy edges and yellow halos, apply MOP (Muriate of Potash) @ 25 kg/acre. If morning dew drops on leaf margins are turbid or milky, it is BLB—temporarily drain standing water and halt urea top-dressing.",
                "likes": 16,
                "is_verified": True,
            }
        ]
    },
    {
        "author_name": "Gurpreet Singh",
        "author_location": "Punjab",
        "crop": "Wheat",
        "crop_icon": "🌾",
        "title": "Yellow stripe-like rust spots appearing after rain",
        "description": "Found linear yellow pustules along leaf veins on upper leaves after recent overcast rainy weather. What fungicide is best before heading stage?",
        "image_url": "/static/images/pests/blast.jpg",
        "tags": "#Yellow Rust, #Wheat, #PAU Guidance",
        "likes": 18,
        "dislikes": 0,
        "answers": [
            {
                "author_name": "Dr. H. S. Dhillon",
                "author_role": "PAU Ludhiana Agronomist",
                "content": "Yellow rust requires swift intervention. Spray Tilt 25 EC (Propiconazole) @ 200 ml in 200 litres of water per acre using a hollow cone nozzle. Spray on a clear, calm morning.",
                "likes": 14,
                "is_verified": True,
            }
        ]
    },
    {
        "author_name": "Zaid Khan",
        "author_location": "Karnataka",
        "crop": "Zucchini",
        "crop_icon": "🥒",
        "title": "Fruit rot and baby zucchini drop in polytunnel",
        "description": "Baby zucchinis turn yellow, soft, and drop before growing past 3 inches. Flowers rot at tips. Is this blossom end rot or lack of pollination?",
        "image_url": "/static/images/pests/verticillium-wilt.jpg",
        "tags": "#Pollination, #Calcium, #Blossom End Rot",
        "likes": 13,
        "dislikes": 0,
        "answers": [
            {
                "author_name": "Sunita Deshmukh",
                "author_role": "Horticultural Consultant",
                "content": "Inside polytunnels without natural bees, unfertilized female fruit aborts and turns yellow. Hand pollinate freshly opened female blooms with male pollen between 7 AM and 9 AM. Also maintain consistent moisture and foliar spray Calcium Chelate @ 1.5 g/L.",
                "likes": 11,
                "is_verified": True,
            }
        ]
    }
]


def ensure_community_seed_data():
    """Ensure initial community posts exist so farmers never see an empty feed."""
    if CommunityPost.objects.exists():
        return

    for item in INITIAL_POSTS:
        answers = item.pop("answers", [])
        post = CommunityPost.objects.create(**item)
        for ans in answers:
            CommunityAnswer.objects.create(
                post=post,
                author_name=ans["author_name"],
                author_role=ans.get("author_role", "Farmer"),
                content=ans["content"],
                likes=ans.get("likes", 0),
                is_verified_solution=ans.get("is_verified", False)
            )

