# NutriScan 🍏

**NutriScan** is a smart nutrition assistant web application that helps users make healthier food choices, fight food insecurity, and support sustainable living.  

---

## 🚀 Features
- 🔍 **Food Search/Scan**: Instantly get nutritional facts by searching for food items.  
- 🤖 **AI Recipes**: Personalized healthy recipe suggestions using AI.  
- 🛒 **Pantry Manager**: Track your stored food items and reduce waste.  
- ❤️ **Donation System**: Integrated with **Stripe** for easy food bank donations.  
- 📚 **Micro-lessons**: Learn about healthy diets and sustainability.

---

## 🛠️ Tech Stack
- **Backend**: Python (Flask)  
- **Database**: SQLAlchemy (SQLite / PostgreSQL for production)  
- **Frontend**: HTML, CSS, JavaScript  
- **Payments**: Stripe API  
- **AI**: OpenAI API (optional for recipe generation)  

---

## 📂 Project Structure
```
NutriScan/
│-- app.py              # Main Flask app
│-- models.py           # Database models
│-- templates/          # HTML templates (Jinja2)
│-- static/             # CSS, JS, Images
│-- requirements.txt    # Dependencies
│-- Procfile            # For deployment
│-- README.md           # Project docs
```

---

## ⚡ Installation & Setup
1. Clone the repository:
   ```bash
   git clone https://github.com/JSIMBA11/nutriscan.git
   cd nutriscan
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate   # (Linux/Mac)
   venv\Scripts\activate    # (Windows)
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file in the project root with:
   ```
   STRIPE_SECRET_KEY=your_stripe_secret
   STRIPE_PUBLISHABLE_KEY=your_stripe_publishable
   OPENAI_API_KEY=your_openai_key (optional)
   DATABASE_URL=sqlite:///nutriscan.db
   ```

5. Run the app locally:
   ```bash
   python app.py
   ```

6. Visit `http://127.0.0.1:5000` in your browser 🚀

---


---

## 💡 Future Improvements
- 📱 Mobile-first UI optimization  
- 🥗 Advanced meal planning with calorie tracking  
- 🌐 Multilingual support for wider accessibility  
- 🧾 AI-powered grocery shopping assistant  

---

## 👨‍💻 Author
-Jerald Simba 

---

## 📜 License
This project is licensed under the GENERAL PUBLIC LICENSE  
