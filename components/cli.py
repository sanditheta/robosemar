import argparse

class CLI:
    @staticmethod
    def parse_args() -> argparse.Namespace:
        parser = argparse.ArgumentParser(description='Voice Interaction with Dialogflow')
        parser.add_argument('--test-mic', action='store_true', help='Test the microphone')
        parser.add_argument('--detect-speech', action='store_true', help='Detect speech')
        parser.add_argument('--chatbot', action='store_true', help='Interact with Chatbot')
        args = parser.parse_args()
        return args
    
    @staticmethod
    def show_usage():
        """Show the usage instructions."""
        print("Usage: python main.py --[test-mic|detect-speech|chatbot]")
