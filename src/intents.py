"""Final intent taxonomy for AppleSupport (11 = 10 + other). Grounded in data_quality scan."""
INTENTS = [
    "software_update",
    "battery_power",
    "connectivity",
    "apple_id_icloud",
    "apps_media",
    "hardware_device",
    "setup_transfer_restore",
    "purchase_billing_service",
    "howto_guidance",
    "support_access_followup",
    "other_out_of_scope",
]

DESCRIPTIONS = {
    "software_update": "iOS/macOS update download, install failure, post-update slowness, freeze, autocorrect bug",
    "battery_power": "battery drain, charging, shutdown, power, overheating",
    "connectivity": "wifi, bluetooth, cellular, carrier, airdrop, hotspot, airpods pairing",
    "apple_id_icloud": "Apple ID, iCloud, password, login, activation lock, backup sync",
    "apps_media": "App Store, Apple Music, iTunes, Photos, Camera app, Safari, Mail app behavior",
    "hardware_device": "screen, button, camera hardware, speaker, mic, water damage, cracked, Mac/iPhone/iPad hardware",
    "setup_transfer_restore": "new device setup, data transfer, restore from backup, migration",
    "purchase_billing_service": "warranty, AppleCare, repair, Genius Bar, refund, billing, store",
    "howto_guidance": "how do I / how to use feature, settings guidance",
    "support_access_followup": "DM follow-up, short ack (yes/both/sent), thanks/closure, link-only needing context",
    "other_out_of_scope": "vague, non-English, non-Apple, jailbreak, unrelated",
}

# Keyword weak-label rules (lowercase, ordered — first match wins except followup handled carefully)
KEYWORDS = {
    "software_update": ["ios 11", "ios11", "update", "updating", "upgrade", "installing", "download stuck", "autocorrect", "i→a", "11.1", "11.0", "software update", "stuck on apple logo after update", "slow after update", "freeze after update"],
    "battery_power": ["battery", "drain", "dies quickly", "won't charge", "not charging", "shuts off", "shutting down", "overheat", "hot iphone", "power off", "charged 100"],
    "connectivity": ["wifi", "wi-fi", "bluetooth", "cellular", "no service", "carrier", "airdrop", "hotspot", "airpods", "pairing", "lte", "signal", "connect"],
    "apple_id_icloud": ["apple id", "icloud", "password", "locked out", "activation lock", "two-factor", "2fa", "sign in", "login", "account"],
    "apps_media": ["app store", "apple music", "itunes", "photos app", "camera app", "safari", "mail app", "imessage", "facetime", "siri", "music won't play", "app crash"],
    "hardware_device": ["screen", "cracked", "display", "flicker", "button", "home button", "camera", "speaker", "mic", "microphone", "water damage", "dropped", "macbook", "keyboard", "trackpad"],
    "setup_transfer_restore": ["setup", "transfer", "restore", "backup", "migrat", "new iphone", "new phone", "icloud backup", "itunes backup"],
    "purchase_billing_service": ["refund", "charged", "billing", "receipt", "warranty", "applecare", "genius bar", "repair", "replace", "store", "appointment", "cost"],
    "howto_guidance": ["how do i", "how to", "how can i", "where is", "where do i", "tutorial", "guide me", "help me use"],
    "support_access_followup": ["dm sent", "sent dm", "just sent", "check dm", "thank", "thanks", "thx", "appreciated", "yes", "both", "done", "ok i", "here is my"],
}

TEMPLATES = {
    "software_update": "Thanks for flagging the update issue. Check Settings > General > About for your iOS version, then try a forced restart. DM us your iOS version + device model and we can look into this together. <BRAND-KB:update>",
    "battery_power": "Sorry your battery is draining fast. Check Settings > Battery to see top usage, try Low Power Mode + background refresh off. DM us your device + iOS version and recent change (e.g. update) so we can dig in. <BRAND-KB:battery>",
    "connectivity": "Let's sort the connection issue. Toggle Wi-Fi/Bluetooth off/on, Forget This Network and rejoin, then restart. DM us your network type + iOS version if it persists. <BRAND-KB:connectivity>",
    "apple_id_icloud": "We can help with the account issue. Try iforgot.apple.com to reset, then Settings > [your name] to re-sign. Don't share passwords here — DM us and we'll guide you securely. <BRAND-KB:account>",
    "apps_media": "Sorry the app/media isn't working. Force-close the app, check App Store for updates, then restart. DM us the app name + iOS version + error text if it continues. <BRAND-KB:apps>",
    "hardware_device": "Sorry about the hardware issue. Note when it started + any damage, back up if you can, then try a restart. DM us device model + photos/description and we'll advise on service options. <BRAND-KB:hardware>",
    "setup_transfer_restore": "Let's get setup/restore working. Keep both devices on Wi-Fi + power, use Quick Start or iCloud/iTunes backup restore. DM us where it stalls (step + error) and we'll walk through it. <BRAND-KB:setup>",
    "purchase_billing_service": "We can point you on warranty/service. Check coverage at checkcoverage.apple.com, back up your device, then book via Apple Support app. DM us device + issue and we'll advise next steps (no payment details here). <BRAND-KB:service>",
    "howto_guidance": "Happy to guide you. Tell us your device + iOS version (Settings > General > About) and the exact step you're stuck on, and we'll share steps. <BRAND-KB:howto>",
    "support_access_followup": "Thanks for following up — we got it. If you sent a DM, we'll review and reply there. Otherwise DM us your device + iOS version + detail and we'll continue. <BRAND-KB:followup>",
    "other_out_of_scope": "Thanks for reaching out. Please DM us a brief description + device + iOS version (Settings > General > About) so we can point you correctly. Don't share personal info publicly. <BRAND-KB:triage>",
}

# Escalation-prone intents (policy review first)
SENSITIVE_INTENTS = {"apple_id_icloud", "purchase_billing_service", "hardware_device", "setup_transfer_restore"}
