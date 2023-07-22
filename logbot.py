from discord import SyncWebhook
webhookUrl = ""
webhook = SyncWebhook.from_url(webhookUrl)

def logs(message, log_to_discord=True):
    print(message)
    if log_to_discord:
        try:
            webhook.send(message)
        except:
            pass
