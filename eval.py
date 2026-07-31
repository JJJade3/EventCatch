import asyncio
from extractor import extract_and_clean

golden_dataset = [
    {
        "post": "Sunset Rooftop Yoga + Chill 🧘 Sat Aug 2, 6pm @ The Nest rooftop, 445 Grand Ave. $25 early bird / $35 door. linktr.ee/nestyoga",
        "expected": {
            "event_name": "Sunset Rooftop Yoga + Chill",
            "date": "Aug 2",
            "location": "The Nest rooftop, 445 Grand Ave",
            "start_time": "6pm",
            "ticket_tiers": [
                {"tier_name": "early bird", "price": 25},
                {"tier_name": "door", "price": 35}],
            "registration_link": "linktr.ee/nestyoga",
        }
    },
    {
        "post": "📚 Indie Book Swap! Sunday Aug 3, 2-5pm at Grounded Cafe (12 Oak St). Free entry, bring a book take a book ☕",
        "expected": {
            "event_name": "Indie Book Swap",
            "date": "Aug 3",
            "location": "Grounded Cafe (12 Oak St)",
            "start_time": "2pm",
            "end_time": "5pm",
        }
    },
    {
        "post": "LATE NIGHT RAMEN POP-UP 🍜 Fri Aug 1 from 9pm till we sell out. Miso Bar, 88 Kent Ave. $18 a bowl, cash only",
        "expected": {
            "event_name": "LATE NIGHT RAMEN POP-UP",
            "date": "Aug 1",
            "location": "Miso Bar, 88 Kent Ave",
            "start_time": "9pm",
            "ticket_tiers": [
                {"tier_name": "a bowl", "price": 18}
            ]
        }
    }
]

def normalize(value):
    value = str(value).lower().strip()
    return value

def fields_match(expected_value, actual_value):
    return normalize(expected_value) == normalize(actual_value)

def compare_record(expected, actual):
    total = 0 
    correct = 0 
    mismatches = []
    
    for field_name in expected:
        total += 1
        if field_name in actual:
            if normalize(expected[field_name]) == normalize(actual[field_name]):
                correct += 1 
            else:
                mismatches.append((field_name, expected[field_name], actual[field_name]))
    
    return correct, total, mismatches


async def run_eval():
    total_correct = 0
    total_fields = 0
    
    for item in golden_dataset:
        post = item["post"]
        expected = item["expected"]
        
        actual = await extract_and_clean(post)
        
        correct, total, mismatches = compare_record(expected, actual)
        
        total_correct += correct
        total_fields += total
        
        print(f"Post: {post[:40]}...")
        print(f"  {correct}/{total} fields correct")
        if mismatches:
            print("  Mismatches:")
            for field_name, expected_value, actual_value in mismatches:
                print(f"    {field_name}: expected '{expected_value}', got '{actual_value}'")
    
    accuracy = total_correct / total_fields
    print(f"\nOverall accuracy: {total_correct}/{total_fields} = {accuracy:.1%}")

asyncio.run(run_eval())
