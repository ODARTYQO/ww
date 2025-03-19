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

    def get_csrf_token(self):
        """
        קבלת CSRF token מהשרת
        """
        try:
            response = self.session.get(
                f"{self.base_url}/api/config",
                headers=self.headers
            )
            if response.ok:
                data = response.json()
                self.csrf_token = data.get('csrf_token')
                if self.csrf_token:
                    self.headers['x-csrf-token'] = self.csrf_token
                    print("התקבל CSRF token")
                    return True
            return False
        except Exception as e:
            print(f"שגיאה בקבלת CSRF token: {str(e)}")
            return False

    def login(self, username, password):
        """
        התחברות למערכת NodeBB
        """
        try:
            print(f"מתחבר למערכת עם המשתמש: {username}")
            
            if not self.get_csrf_token():
                print("לא הצלחנו לקבל CSRF token")
                return False
            
            login_data = {
                "username": username,
                "password": password
            }
            
            response = self.session.post(
                f"{self.base_url}/api/v3/utilities/login",
                json=login_data,
                headers=self.headers
            )
            
            if response.ok:
                data = response.json()
                if data.get('status', {}).get('code') == 'ok':
                    self.uid = data.get('response', {}).get('uid')
                    print("התחברות הצליחה!")
                    return True
            
            print(f"התחברות נכשלה. קוד תגובה: {response.status_code}")
            print(f"תוכן התגובה: {response.text}")
            return False
            
        except Exception as e:
            print(f"שגיאה בהתחברות: {str(e)}")
            return False

    def vote_post(self, post_id, vote_type="upvote"):
        """
        הצבעה על פוסט
        """
        if not self.csrf_token:
            print("נדרש CSRF token!")
            return False

        try:
            if vote_type not in ["upvote", "downvote"]:
                print("סוג הצבעה לא חוקי. יש להשתמש ב-upvote או downvote")
                return False

            print(f"מצביע על פוסט {post_id} ({vote_type})")
            
            response = self.session.post(
                f"{self.base_url}/api/v3/posts/{post_id}/vote",
                json={"delta": 1 if vote_type == "upvote" else -1},
                headers=self.headers
            )

            if response.ok:
                result = response.json()
                if result.get('status', {}).get('code') == 'ok':
                    print(f"ההצבעה בוצעה בהצלחה!")
                    return True
                else:
                    print(f"שגיאה בהצבעה: {result}")
            else:
                print(f"שגיאה בהצבעה. קוד: {response.status_code}")
                print(f"תוכן: {response.text}")
            
            return False

        except Exception as e:
            print(f"שגיאה בהצבעה: {str(e)}")
            return False

    def reply_to_post(self, topic_id, content, reply_to_pid=None):
        """
        יצירת תגובה לפוסט ספציפי
        """
        if not self.csrf_token:
            print("נדרש CSRF token!")
            return False

        try:
            data = {
                "tid": int(topic_id),
                "content": content,
                "_uid": self.uid
            }
            
            if reply_to_pid:
                data["toPid"] = int(reply_to_pid)

            print(f"שולח תגובה לנושא {topic_id}" + 
                  (f" (בתגובה לפוסט {reply_to_pid})" if reply_to_pid else ""))

            response = self.session.post(
                f"{self.base_url}/api/v3/posts",
                json=data,
                headers=self.headers
            )

            if response.ok:
                result = response.json()
                if result.get('status', {}).get('code') == 'ok':
                    post_data = result.get('response')
                    print(f"התגובה נוצרה בהצלחה! מזהה: {post_data.get('pid')}")
                    return post_data
                else:
                    print(f"שגיאה בתגובת השרת: {result}")
            else:
                print(f"שגיאה ביצירת תגובה. קוד: {response.status_code}")
                print(f"תוכן: {response.text}")
            
            return None

        except Exception as e:
            print(f"שגיאה ביצירת תגובה: {str(e)}")
            return None

    def create_topic(self, category_id, title, content):
        """
        יצירת נושא חדש בקטגוריה
        """
        if not self.csrf_token:
            print("נדרש CSRF token!")
            return False

        try:
            data = {
                "cid": int(category_id),
                "title": title,
                "content": content,
                "tags": [],
                "_uid": self.uid
            }

            print(f"שולח בקשה ליצירת נושא בקטגוריה {category_id}...")
            print(f"כותרת: {title}")
            print(f"תוכן: {content[:100]}...")

            response = self.session.post(
                f"{self.base_url}/api/v3/topics",
                json=data,
                headers=self.headers
            )

            if response.ok:
                result = response.json()
                if result.get('status', {}).get('code') == 'ok':
                    topic_data = result.get('response')
                    print(f"נושא חדש נוצר בהצלחה! מזהה: {topic_data.get('tid')}")
                    return topic_data
                else:
                    print(f"שגיאה בתגובת השרת: {result}")
            else:
                print(f"תוכן תגובת השגיאה: {response.text}")
            
            return None

        except Exception as e:
            print(f"שגיאה ביצירת נושא: {str(e)}")
            return None

    def get_topic_info(self, topic_url):
        """
        מקבל מידע על נושא מתוך URL
        """
        try:
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

    def extract_post_id_from_url(self, url):
        """
        מחלץ את מזהה הפוסט מתוך URL
        """
        try:
            # אם זה קישור ישיר לפוסט
            if '/post/' in url:
                post_id = url.split('/post/')[1].split('/')[0]
                print(f"נמצא מזהה פוסט מהקישור: {post_id}")
                return post_id
            
            # אם יש # בקישור
            if '#' in url:
                post_id = url.split('#')[1]
                print(f"נמצא מזהה פוסט מהקישור: {post_id}")
                return post_id
                
            return None
        except Exception as e:
            print(f"שגיאה בחילוץ מזהה פוסט: {str(e)}")
            return None
        
    def get_post_info(self, post_id):
        """
        מקבל מידע על פוסט ספציפי עם הדפסת דיבאג מלאה
        """
        try:
            print(f"\nמנסה לקבל מידע על פוסט {post_id}...")
            
            # נתיב API ראשון
            url = f"{self.base_url}/api/v3/posts/{post_id}"
            print(f"מנסה URL ראשון: {url}")
            
            response = self.session.get(url, headers=self.headers)
            print(f"קוד תגובה: {response.status_code}")
            print(f"Headers: {dict(response.headers)}")
            
            try:
                response_text = response.text
                print(f"תוכן תגובה גולמי: {response_text[:500]}")  # מציג עד 500 תווים
                
                # בדיקה האם התוכן הוא JSON תקין
                if response.ok:
                    try:
                        data = response.json()
                        print(f"JSON מפוענח: {data}")
                        return data
                    except ValueError as e:
                        print(f"לא ניתן לפענח כ-JSON: {str(e)}")
            except Exception as e:
                print(f"שגיאה בקריאת תוכן התגובה: {str(e)}")
            
            # נתיב API שני
            alt_url = f"{self.base_url}/api/post/{post_id}"
            print(f"\nמנסה URL שני: {alt_url}")
            
            alt_response = self.session.get(alt_url, headers=self.headers)
            print(f"קוד תגובה: {alt_response.status_code}")
            print(f"Headers: {dict(alt_response.headers)}")
            
            try:
                alt_response_text = alt_response.text
                print(f"תוכן תגובה גולמי: {alt_response_text[:500]}")
                
                if alt_response.ok:
                    try:
                        data = alt_response.json()
                        print(f"JSON מפוענח: {data}")
                        return data
                    except ValueError as e:
                        print(f"לא ניתן לפענח כ-JSON: {str(e)}")
            except Exception as e:
                print(f"שגיאה בקריאת תוכן התגובה: {str(e)}")
            
            print("\nשני הניסיונות נכשלו")
            return None
                
        except Exception as e:
            print(f"שגיאה כללית: {str(e)}")
            print(f"סוג השגיאה: {type(e)}")
            return None

    def vote_post(self, post_id, vote_type="upvote"):
        """
        הצבעה על פוסט - גרסה מעודכנת
        """
        if not self.csrf_token:
            print("נדרש CSRF token!")
            return False

        try:
            print(f"\nמנסה להצביע על פוסט {post_id} ({vote_type})...")
            
            # עדכון ה-headers עם כל השדות הנדרשים
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'application/json, text/plain, */*',
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-Requested-With': 'XMLHttpRequest',
                'Origin': 'https://mitmachim.top',
                'Referer': f'https://mitmachim.top/post/{post_id}',
                'x-csrf-token': self.csrf_token,
                'Connection': 'keep-alive',
                'Sec-Fetch-Dest': 'empty',
                'Sec-Fetch-Mode': 'cors',
                'Sec-Fetch-Site': 'same-origin'
            }

            # ניסיון ראשון - נתיב חדש
            url = f"{self.base_url}/api/v3/posts/{post_id}/vote"
            data = {
                'delta': '1' if vote_type == 'upvote' else '-1'
            }
            
            print(f"שולח בקשת POST ל: {url}")
            print(f"Headers: {headers}")
            print(f"Data: {data}")
            
            response = self.session.post(
                url,
                data=data,
                headers=headers
            )
            
            print(f"\nתגובה התקבלה:")
            print(f"קוד תגובה: {response.status_code}")
            print(f"Headers: {dict(response.headers)}")
            print(f"תוכן תגובה: {response.text}")
            
            if response.ok:
                try:
                    result = response.json()
                    if isinstance(result, dict):
                        if result.get('status', {}).get('code') == 'ok':
                            print("ההצבעה הצליחה!")
                            return True
                except:
                    pass

            # ניסיון שני - נתיב ישן
            url = f"{self.base_url}/api/post/vote"
            data = {
                'pid': str(post_id),
                'delta': '1' if vote_type == 'upvote' else '-1'
            }
            
            print(f"\nמנסה שיטה חלופית...")
            print(f"שולח בקשת POST ל: {url}")
            print(f"Data: {data}")
            
            response = self.session.post(
                url,
                data=data,
                headers=headers
            )
            
            print(f"\nתגובה התקבלה:")
            print(f"קוד תגובה: {response.status_code}")
            print(f"תוכן תגובה: {response.text}")
            
            if response.ok:
                try:
                    result = response.json()
                    if isinstance(result, dict) and 'error' not in result:
                        print("ההצבעה הצליחה (דרך API חלופי)!")
                        return True
                except:
                    pass

            # ניסיון שלישי - נתיב נוסף
            url = f"{self.base_url}/api/v3/posts/{post_id}/{'upvote' if vote_type == 'upvote' else 'downvote'}"
            
            print(f"\nמנסה שיטה שלישית...")
            print(f"שולח בקשת POST ל: {url}")
            
            response = self.session.post(
                url,
                headers=headers
            )
            
            print(f"\nתגובה התקבלה:")
            print(f"קוד תגובה: {response.status_code}")
            print(f"תוכן תגובה: {response.text}")
            
            if response.ok:
                try:
                    result = response.json()
                    if isinstance(result, dict) and result.get('status', {}).get('code') == 'ok':
                        print("ההצבעה הצליחה (דרך API שלישי)!")
                        return True
                except:
                    pass

            print("\nכל הניסיונות נכשלו")
            return False

        except Exception as e:
            print(f"שגיאה כללית: {str(e)}")
            print(f"סוג השגיאה: {type(e)}")
            return False

    def interactive_vote(self):
        print("\n=== הצבעה על פוסט ===")
        
        while True:
            url = input("\nהדבק את הקישור לפוסט (או הקש Enter לחזרה): ")
            if not url:
                return
            
            # ניסיון לחלץ את מזהה הפוסט מהקישור
            post_id = None
            
            if '/post/' in url:
                post_id = url.split('/post/')[1].split('/')[0]
            elif '#' in url:
                post_id = url.split('#')[1]
            
            if not post_id:
                post_id = input("\nלא נמצא מזהה בקישור. אנא הכנס מזהה פוסט ידנית: ")
            
            print(f"\nמזהה פוסט שנמצא: {post_id}")
            
            vote_type = ""
            while vote_type not in ["upvote", "downvote"]:
                vote_type = input("\nסוג ההצבעה (upvote/downvote): ").lower()
                if vote_type not in ["upvote", "downvote"]:
                    print('נא להקליד "upvote" או "downvote" בדיוק')
            
            if self.vote_post(post_id, vote_type):
                print("\nההצבעה הושלמה בהצלחה!")
                return
            
            print("\nההצבעה נכשלה. האם תרצה:")
            print("1. לנסות פוסט אחר")
            print("2. לחזור לתפריט הראשי")
            
            if input("בחירתך (1-2): ") != "1":
                break
        
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
            
            print("\nפוסטים בנושא:")
            for post in topic_info['posts']:
                print(f"מזהה: {post.get('pid')} | מאת: {post.get('user', {}).get('username')} | "
                      f"תוכן: {post.get('content')[:100]}...")

            reply_to = input("\nהכנס את מזהה הפוסט שברצונך להגיב אליו (או הקש Enter לתגובה כללית): ")
            content = input("הכנס את תוכן התגובה:\n")

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
    
    print("=== התחברות למערכת ===")
    username = input("שם משתמש: ")
    password = input("סיסמה: ")
    
    if api.login(username, password):
        api.interactive_menu()
    else:
        print("ההתחברות נכשלה")

if __name__ == "__main__":
    main()
