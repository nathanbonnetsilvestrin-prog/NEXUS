const webpush = require("web-push");

const subscription = JSON.parse(process.env.PUSH_SUBSCRIPTION);

webpush.setVapidDetails(
  "mailto:nexus-notifications@example.com",
  process.env.VAPID_PUBLIC_KEY,
  process.env.VAPID_PRIVATE_KEY
);

const notification = {
  title: "NEXUS Intelligence",
  body: "Votre journal du jour est prêt. Consultez les actualités.",
  url: "https://nexus-journal.github.io/NEXUS/"
};

webpush.sendNotification(
  subscription,
  JSON.stringify(notification)
).then(() => {
  console.log("Notification NEXUS envoyée !");
}).catch(error => {
  console.error("Erreur d'envoi :", error.statusCode, error.body);
  process.exit(1);
});