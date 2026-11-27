// Sends signed-out visitors to the sign-in page. Calls onReady(user) once signed in.
// This only improves the experience: the real protection is the check in the FAQ service.
function requireSignIn(onReady) {
  firebase.auth().onAuthStateChanged((user) => {
    if (!user) {
      window.location.href = "index.html";
      return;
    }
    onReady(user);
  });
}

function signOutAndExit() {
  return firebase.auth().signOut().finally(() => {
    window.location.href = "index.html";
  });
}
