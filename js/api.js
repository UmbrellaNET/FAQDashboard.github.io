// Calls the FAQ service with the signed-in user's Firebase ID token.
// The service checks the token and that the user is an approved admin.
const API_BASE = "https://faq-two-murex.vercel.app";

async function api(path, { method = "GET", body } = {}) {
  const user = firebase.auth().currentUser;
  if (!user) {
    const err = new Error("Not signed in");
    err.status = 401;
    throw err;
  }

  const token = await user.getIdToken();
  const res = await fetch(API_BASE + path, {
    method,
    headers: {
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json"
    },
    body: body === undefined ? undefined : JSON.stringify(body)
  });

  let data = null;
  try { data = await res.json(); } catch (e) { /* empty or non-JSON response */ }

  if (!res.ok) {
    const err = new Error((data && data.error) || `Request failed (${res.status})`);
    err.status = res.status;
    throw err;
  }
  return data;
}
