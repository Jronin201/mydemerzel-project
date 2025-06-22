import os
import json
from campaign_creator import create_campaign

def confirm_and_create_campaign():
    # Path to the campaign file
    campaign_file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "campaign.txt"))
    
    # Ask for user confirmation
    user_confirmation = input("Would you like me to create a new campaign? (yes/no): ").strip().lower()
    
    if user_confirmation in ['yes', 'y', 'sure', 'ok', 'okay']:
        # Delete existing campaign file if it exists
        if os.path.exists(campaign_file_path):
            os.remove(campaign_file_path)
            print("Existing campaign deleted.")
        
        # Create new campaign
        new_campaign = create_campaign()

        # Save the new campaign to a file
        with open(campaign_file_path, 'w') as f:
            json.dump(new_campaign, f, indent=2)
        print("New campaign created and saved to campaign.txt.")

    else:
        print("Campaign creation cancelled.")

def process_user_request(user_request):
    # Check user request for creating a new campaign
    if "create a new campaign" in user_request.lower() or "start a new campaign" in user_request.lower():
        confirm_and_create_campaign()
    else:
        print("Request not recognized for campaign creation.")

if __name__ == "__main__":
    # Simulate a chatbot session
    user_request = input("How can I assist you today? ")
    process_user_request(user_request)
