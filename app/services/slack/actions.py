from app.services.slack.slack import client
from slack_sdk.errors import SlackApiError


def send_INFO_message_to_slack_channel(channel_id, title_message, sub_title, message):
        blocks=[
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*{title_message}*"
                    }
                },
                {
                    "type": "section",
                    "fields": [
                        {
                            "type": "mrkdwn",
                            "text": f"*{sub_title}:*\n{message}"
                        }
                    ]
                },
                {
                "type": "divider"
                }
            ]
    
        try:
            result = client.chat_postMessage(
                channel=channel_id,
                text=title_message, 
                blocks=blocks
            )
            response = result['ok']
            if response == True:
                return f'Message sent successfully to Slack channel {channel_id}', 200

        except SlackApiError as e:
            print(f"Error posting message: {e}")
            return f'Error sending this message: "{title_message}" to Slack channel, Reason:\n{str(e)}', 500

