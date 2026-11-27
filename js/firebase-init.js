// Firebase web configuration. These values identify the project and are safe to publish;
// access is controlled by Firebase Authentication and by the FAQ service, not by hiding them.
const firebaseConfig = {
  apiKey: "AIzaSyBhwvWCdkqmedlYiwTOovz9jPsUevLsaBo",
  authDomain: "umbrellalabs-faq.firebaseapp.com",
  projectId: "umbrellalabs-faq",
  storageBucket: "umbrellalabs-faq.firebasestorage.app",
  messagingSenderId: "123148775588",
  appId: "1:123148775588:web:33d07445cfb29692c27631"
};

if (!firebase.apps.length) {
  firebase.initializeApp(firebaseConfig);
}
