from agent import process_request

test_cases = [
    {
        "name": "Karan Mehta",
        "email": "karan.mehta@veridian-corp.example",
        "request": "I'm locked out of my account, I tried my password 6 times."
    },
    {
        "name": "Aman",
        "email": "aman@veridian-corp.example",
        "request": "Can my guest get Wi-Fi tomorrow?"
    },
    {
        "name": "Sita",
        "email": "sita@veridian-corp.example",
        "request": "I think I received a phishing email."
    }
]

for case in test_cases:
    print(f"\nTesting request from {case['name']}: {case['request']}")
    try:
        result = process_request(case['name'], case['email'], case['request'])
        print(f"Status: {result['status']}")
        print(f"Category: {result['category']}")
        print(f"Response: {result['response']}")
        if result['ticket']:
            print(f"Ticket Created: {result['ticket']['ticket_id']}")
    except Exception as e:
        print(f"Error: {e}")
