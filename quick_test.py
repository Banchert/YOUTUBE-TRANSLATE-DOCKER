import requests
import json

def test_system():
    print("🔍 Testing system status...")
    
    try:
        # Test backend health
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print("✅ Backend is running!")
            print(f"   Status: {data.get('status')}")
            
            services = data.get('services', {})
            for service, status in services.items():
                icon = "✅" if "available" in status.lower() else "⚠️"
                print(f"   {icon} {service}: {status}")
        else:
            print(f"❌ Backend error: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to backend (port 8000)")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    try:
        # Test frontend
        response = requests.get("http://localhost:3000", timeout=5)
        if response.status_code == 200:
            print("✅ Frontend is running!")
        else:
            print(f"⚠️ Frontend error: {response.status_code}")
    except:
        print("❌ Cannot connect to frontend (port 3000)")

if __name__ == "__main__":
    test_system() 