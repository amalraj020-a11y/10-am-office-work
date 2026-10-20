We are creating a one-page website for Mrs. Wilson's Cafe in Kolkata.
 We have the following facts from the provided JSON:
   - business_name: "Mrs. Wilson's Cafe"
   - category: "cafe"
   - city_area: "Kolkata - Jodhpur Park"
   - phone: "+91 : 91674 19756"
   - public_email: "" (so we won't use an email in the copy)
   - social_url: "https://www.instagram.com/mrswilsonscafe/"
   - address: "P-174, Jodhpur Park, Kolkata, West Bengal 700068, India"
   - hours: "Mon 1 PM–8 PM; Tue–Sat 12 PM–9 PM; Sun 12:30 PM–9 PM"
   - services: ["home-style continental food", "Asian dishes", "coffee", "desserts", "cat cafe experience"]
   - website_evidence: "Public listing reviewed: https://catcafemap.com/cat-cafe/mrs-wilsons-cafe-kolkata. Listing identifies Instagram as the website/social presence; no dedicated official domain was found in the search performed. Confirm with owner before production."
   - source_urls: ["https://catcafemap.com/cat-cafe/mrs-wilsons-cafe-kolkata"]

 Important: We must not invent any reviews, ratings, founders, prices, claims, or services. We have the services list.

 We are to create:
   - title: a short title for the website
   - intro: a short introductory paragraph
   - cards: an array of 4 objects, each with label, title, description
   - email_subject: a subject line for an email
   - email_body: the body of the email (we don't have an email address, but we can write a generic email body that includes the business info)
   - whatsapp_body: the body of the WhatsApp message (short and friendly)

 Steps:

 1. Title: Should be catchy and include the business name. Example: "Mrs. Wilson's Cafe: Your Go-To Spot for Coffee and Cats in Kolkata"

 2. Intro: A short paragraph that introduces the cafe. We have the services and location. We can say: 
    "Nestled in the heart of Kolkata's Jodhpur Park, Mrs. Wilson's Cafe is a charming spot where you can savor home-style continental dishes, Asian specialties, and delicious coffee. Our unique cat cafe experience adds a playful twist to your visit."

 3. Cards: We need 4 cards. We can structure them as:
    a. Location (with address and city area)
    b. Hours (with the hours string)
    c. Services (we have 5 services, so we can group or pick 4? But note: we must not invent. We have the list. We can do: 
        - Card 1: Location
        - Card 2: Hours
        - Card 3: Services (we can list 4 of the 5? But the problem says: do not invent. We have 5 services. We can write a description that covers the services without listing all? Or we can have one card for services? But the requirement says 4 cards. Let's think of 4 distinct aspects.)

    Alternatively, we can do:
      Card 1: Location
      Card 2: Hours
      Card 3: Services (with a short description of the services, e.g., "We serve home-style continental food, Asian dishes, coffee, desserts, and have a cat cafe experience.")
      Card 4: Contact (with phone and social media)

    However, note: the problem says "original marketing copy" and we must use only the verified facts.

    Let's plan the 4 cards:

      Card 1: 
        label: "Location"
        title: "Kolkata's Jodhpur Park Gem"
        description: "P-174, Jodhpur Park, Kolkata, West Bengal 700068, India"

      Card 2:
        label: "Hours"
        title: "Open Daily for Your Coffee Fix"
        description: "Mon 1 PM–8 PM