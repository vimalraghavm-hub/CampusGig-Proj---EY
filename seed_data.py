import os
import django
import random
from decimal import Decimal

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'campusgig.settings')
django.setup()

from django.contrib.auth import get_user_model
from platform_app.models import Category, Gig, Order, Review, Message

User = get_user_model()

def seed():
    print("Starting data seeding...")

    # 1. Create Categories
    categories_data = [
        {'name': 'Web Development', 'icon': 'fas fa-code', 'slug': 'web-development'},
        {'name': 'Graphic Design', 'icon': 'fas fa-paint-brush', 'slug': 'graphic-design'},
        {'name': 'Content Writing', 'icon': 'fas fa-pen-nib', 'slug': 'content-writing'},
        {'name': 'App Development', 'icon': 'fas fa-mobile-alt', 'slug': 'app-development'},
        {'name': 'Video Editing', 'icon': 'fas fa-video', 'slug': 'video-editing'},
        {'name': 'Digital Marketing', 'icon': 'fas fa-bullhorn', 'slug': 'digital-marketing'},
    ]

    categories = []
    for cat in categories_data:
        c, created = Category.objects.get_or_create(slug=cat['slug'], defaults={'name': cat['name'], 'icon': cat['icon']})
        categories.append(c)
        if created:
            print(f"Created Category: {cat['name']}")

    # 2. Create Users (Sellers & Buyers)
    # Ensure we have a superuser first
    if not User.objects.filter(is_superuser=True).exists():
        User.objects.create_superuser('admin', 'admin@example.com', '12345678')
        print("Created Superuser: admin")

    usernames = ['ananya', 'rahul', 'priya', 'arjun', 'sneha', 'vikram', 'kavita', 'ishaan', 'rohan', 'meera']
    users = []
    for uname in usernames:
        user, created = User.objects.get_or_create(username=uname, defaults={'email': f"{uname}@example.com"})
        if created:
            user.set_password('12345678')
            user.save()
            print(f"Created User: {uname}")
        users.append(user)

    # 3. Create Gigs
    gig_templates = [
        ("I will build a professional React website", "Need a modern, responsive website? I specialize in React and Tailwind CSS to build high-performance web applications for your startup.", 150, 7),
        ("I will design a premium logo for your brand", "Get a unique, high-quality logo that stands out. Professional vector designs with unlimited revisions.", 45, 3),
        ("I will write SEO-optimized blog posts", "Rank higher on Google with expertly written articles tailored to your niche. 1000+ words per post.", 30, 2),
        ("I will create a stunning 2D explainer video", "Engage your audience with professional animations and voiceovers. Perfect for marketing.", 200, 10),
        ("I will develop your custom Android app", "From concept to Play Store. High-quality Flutter or Native Android development.", 500, 14),
        ("I will manage your Instagram for a month", "Boost your engagement and following with curated posts, stories, and growth strategies.", 100, 30),
        ("I will edit your YouTube videos professionally", "Fast cuts, color grading, sound design, and engaging subtitles for your channel.", 60, 4),
        ("I will design attractive UI/UX for your mobile app", "User-centric designs with high-fidelity prototypes using Figma or Adobe XD.", 250, 7),
    ]

    all_gigs = []
    for i in range(30):
        template = random.choice(gig_templates)
        category = random.choice(categories)
        user = random.choice(users[:5]) # First 5 are sellers
        
        gig = Gig.objects.create(
            user=user,
            category=category,
            title=f"{template[0]} - {i}",
            description=template[1],
            price=Decimal(template[2]) + random.randint(-10, 50),
            delivery_time=template[3] + random.randint(-1, 3),
        )
        all_gigs.append(gig)
    print(f"Created {len(all_gigs)} Gigs.")

    # 4. Create Orders & Reviews
    statuses = ['completed', 'completed', 'completed', 'in_progress', 'pending']
    review_comments = [
        "Excellent work! Very professional and delivered on time.",
        "Communication was great, and the result was better than expected.",
        "A bit late but the quality made up for it. Highly recommended.",
        "Truly talented student. Will definitely hire again!",
        "Perfect execution of my requirements. Thank you, Rahul!",
        "Saved me a lot of time. Great value for money.",
    ]

    for i in range(50):
        gig = random.choice(all_gigs)
        client = random.choice(users[5:]) # Last 5 are buyers
        status = random.choice(statuses)
        
        order = Order.objects.create(
            gig=gig,
            client=client,
            status=status
        )
        
        # Add Review if completed
        if status == 'completed':
            Review.objects.create(
                order=order,
                rating=random.randint(4, 5),
                comment=random.choice(review_comments)
            )
            
    print("Created 50 Orders with random Reviews.")

    # 5. Add Messages
    test_order = Order.objects.first()
    Message.objects.create(
        order=test_order,
        sender=test_order.client,
        receiver=test_order.gig.user,
        content="Hi! I'm interested in your service. Can we discuss the requirements?"
    )
    Message.objects.create(
        order=test_order,
        sender=test_order.gig.user,
        receiver=test_order.client,
        content="Sure! I'd love to help. What do you have in mind?"
    )
    print("Added sample messages.")

    print("\nSeeding finished successfully! All pages will now show realistic data.")

if __name__ == '__main__':
    seed()
