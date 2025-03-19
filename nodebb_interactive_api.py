import requests
import json
import urllib3
from datetime import datetime
import sys

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class NodeBBInteractiveAPI:
    def __init__(self):
        self.base_url = "https://mitmachim.top"
        self.session = requests.Session()
        self.session.verify = False
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'X-Requested-With': 'XMLHttpRequest',
            'Origin': 'https://mitmachim.top',
            'Referer': 'https://mitmachim.top/'
        }
        self.csrf_token = None
        self.uid = None

    # [קוד מקורי של התחברות וCSRF נשאר כפי שהיה]

    def get_topic_info(self, topic_url):
        """
        מקבל מידע על נושא מתוך URL
        """
        try:
            # מנסה לחלץ את מזהה הנושא מה-URL
            topic_id = topic_url.split('topic/')[1].split('/')[0]
            response = self.session.get(
                f"{self.base_url}/api/topic/{topic_id}",
                headers=self.headers
            )
            
            if response.ok:
                data = response.json()
                return {
                    'tid': topic_id,
                    'title': data.get('title'),
                    'posts': data.get('posts', [])
                }
            return None
        except Exception as e:
            print(f"שגיאה בקבלת מידע על הנושא: {str(e)}")
            return None

    def interactive_menu(self):
        while True:
            print("\n=== תפריט פעולות בפורום ===")
            print("1. הצבעה על פוסט")
            print("2. תגובה לפוסט")
            print("3. יצירת נושא חדש")
            print("4. יציאה")
            
            choice = input("\nבחר פעולה (1-4): ")
            
            if choice == "1":
                self.interactive_vote()
            elif choice == "2":
                self.interactive_reply()
            elif choice == "3":
                self.interactive_create_topic()
            elif choice == "4":
                print("להתראות!")
                break
            else:
                print("בחירה לא חוקית, נסה שנית")

    def interactive_vote(self):
        print("\n=== הצבעה על פוסט ===")
        post_url = input("הדבק את הקישור לפוסט (או הקש Enter לחזרה): ")
        if not post_url:
            return

        try:
            # חילוץ מזהה הפוסט מה-URL
            post_id = post_url.split('#')[1] if '#' in post_url else input("הכנס את מזהה הפוסט: ")
            
            vote_type = ""
            while vote_type not in ["upvote", "downvote"]:
                vote_type = input("סוג ההצבעה (upvote/downvote): ").lower()
            
            if self.vote_post(post_id, vote_type):
                print("ההצבעה בוצעה בהצלחה!")
            else:
                print("ההצבעה נכשלה")
        except Exception as e:
            print(f"שגיאה: {str(e)}")

    def interactive_reply(self):
        print("\n=== תגובה לפוסט ===")
        topic_url = input("הדבק את הקישור לנושא (או הקש Enter לחזרה): ")
        if not topic_url:
            return

        try:
            topic_info = self.get_topic_info(topic_url)
            if not topic_info:
                print("לא נמצא מידע על הנושא")
                return

            print(f"\nנושא: {topic_info['title']}")
            
            # הצגת הפוסטים בנושא
            print("\nפוסטים בנושא:")
            for post in topic_info['posts']:
                print(f"מזהה: {post.get('pid')} | מאת: {post.get('user', {}).get('username')} | "
                      f"תוכן: {post.get('content')[:100]}...")

            reply_to = input("\nהכנס את מזהה הפוסט שברצונך להגיב אליו (או הקש Enter לתגובה כללית): ")
            content = input("הכנס את תוכן התגובה:\n")

            # הוספת פורמט HTML בסיסי
            formatted_content = f"<p>{content}</p>"
            
            result = self.reply_to_post(
                topic_info['tid'],
                formatted_content,
                reply_to if reply_to else None
            )

            if result:
                print("התגובה נשלחה בהצלחה!")
            else:
                print("שליחת התגובה נכשלה")

        except Exception as e:
            print(f"שגיאה: {str(e)}")

    def interactive_create_topic(self):
        print("\n=== יצירת נושא חדש ===")
        
        # הצגת רשימת הקטגוריות
        try:
            response = self.session.get(
                f"{self.base_url}/api/categories",
                headers=self.headers
            )
            if response.ok:
                categories = response.json()
                print("\nקטגוריות זמינות:")
                for cat in categories:
                    print(f"מזהה: {cat.get('cid')} | שם: {cat.get('name')}")
            
            category_id = input("\nהכנס את מזהה הקטגוריה: ")
            title = input("הכנס כותרת לנושא: ")
            content = input("הכנס את תוכן ההודעה:\n")

            # הוספת פורמט HTML בסיסי ומידע על היוצר
            current_time = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
            formatted_content = f"""
            <p>{content}</p>
            <hr>
            <p><small>נוצר על ידי API ב-{current_time} UTC</small></p>
            """
            
            result = self.create_topic(int(category_id), title, formatted_content)
            if result:
                print(f"הנושא נוצר בהצלחה! קישור: {self.base_url}/topic/{result.get('tid')}")
            else:
                print("יצירת הנושא נכשלה")

        except Exception as e:
            print(f"שגיאה: {str(e)}")

def main():
    api = NodeBBInteractiveAPI()
    
    # קבלת פרטי התחברות
    print("=== התחברות למערכת ===")
    username = input("שם משתמש: ")
    password = input("סיסמה: ")
    
    if api.login(username, password):
        api.interactive_menu()
    else:
        print("ההתחברות נכשלה")

if __name__ == "__main__":
    main()