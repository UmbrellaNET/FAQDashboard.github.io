# FAQ Dashboard 

The admin dashboard for the UmbrellaNET FAQ assistant and its live chat widget. It is a static website, hosted on Vercel. Team members sign in with Firebase Authentication, then browse saved conversations, check usage analytics, take over chats as a live agent and follow up on missed agent requests.

Live site: https://umbrellanet.github.io/FAQDashboard.github.io/
Backend: https://github.com/UmbrellaNET/FAQ


## Contents

- [How it works](#how-it-works)
- [Pages](#pages)
- [Data model](#data-model)
- [How it was built](#how-it-was-built)
- [Hosting on Vercel](#hosting-on-vercel)
- [Getting started](#getting-started)
- [Configuration reference](#configuration-reference)
- [Repository layout](#repository-layout)
- [Testing and verification](#testing-and-verification)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)

## How it works

The dashboard is plain HTML, CSS and JavaScript with no build step. The browser loads the pages from Vercel. Sign-in is handled by Firebase Authentication. Conversation history and missed requests are read from an Upstash Redis database that the FAQ service and chat widget write to. Live chat messages between visitors and agents travel over a browser broadcast channel.

What happens to one visit:

1. The visitor opens the sign-in page (`index.html`) and signs in with an email and password, or with Google.
2. On success the page redirects to `index2.html`, the dashboard home, which shows a welcome screen, a calendar and a red badge counting unseen missed agent requests.
3. The side menu leads to Chats, Analytics, Agent and Missed Agent Requests.
4. The badge refreshes on a timer (15 to 60 seconds depending on the page) and straight away when the widget announces a missed request.

## Pages

| Page | Purpose |
| --- | --- |
| `index.html` | Sign-in (email and password, Google) |
| `register.html` | Create an account |
| `forgot-password.html` | Password reset |
| `index2.html` | Dashboard home: welcome, calendar, missed request badge |
| `chats.html` | Read-only view of saved conversations. Lists sessions with message count and a short IP hash, shows messages by date, and finds a session by ID. The reply box is disabled |
| `analytics.html` | Charts and totals: total users, users active in 30 days, conversations, total messages, average messages per conversation, new users, retention, response rate, a monthly bar chart with a date filter, top sessions and message split. Refreshes every 10 minutes |
| `agent.html` | Agent panel for live chat. The agent enters a name, goes online, receives requests with Accept and Deny, chats, and ends the session. Desktop notifications announce new requests |
| `missed.html` | Missed Agent Requests: people who asked for a human when no agent was online [confirm details] |
| `profile.html` | [The signed-in user's profile] |

## Data model

Conversations are stored in Upstash Redis by the FAQ service.

| Key | Type | Content |
| --- | --- | --- |
| `umbrellanet_chat_{ipHash16}_{sessionId}` | List | One JSON item per message: `{ role, text, timestamp? }`. The first two items are the system prompt set-up and are skipped by the dashboard |
| `umbrellanet_missed_requests` | List | One item per missed agent request |
| `umbrellanet_missed_seen` | Set | Identifiers of missed requests already marked as seen |

The unseen badge count is the length of the missed requests list minus the size of the seen set.

Live chat uses the browser broadcast channel `umbrellanet_livechat` with these message types: `AGENT_ONLINE` (sent every 8 seconds), `AGENT_OFFLINE`, `TRANSFER_REQUEST`, `USER_MSG`, `USER_DISCONNECT`, `AGENT_ACCEPT`, `AGENT_DENY`, `AGENT_MSG`, `AGENT_EXIT` and `MISSED_REQUEST`.

The analytics treat one IP hash as one user, so "Total Users" counts unique network addresses, not people. Messages without a timestamp are counted under the current month, and the page shows a warning.

## How it was built

- **Static site on Vercel.** No server to run and no build step. Every push to `main` deploys to production, and every other branch gets a preview address.
- **Firebase Authentication for sign-in.** Email and password, plus Google sign-in, using the Firebase JavaScript SDK (version 9 compat build). The Firebase project is `umbrellalabs-faq`.
- **Direct reads from Upstash Redis.** The Chats, Analytics and badge code call the Upstash REST API from the browser, using SCAN to find sessions and LRANGE to read them.
- **Chart.js** draws the analytics bar chart, loaded from a CDN.
- **Browser desktop notifications** alert an agent to new requests, with an in-page banner asking for permission.
- **Safe rendering.** Message text is escaped before it is shown, then split into paragraphs and line breaks.
- **Templates.** The sign-in and home pages use ready-made templates (one names MACode ID in its header). Keep each template's license notice with the code.

## Hosting on Vercel

Both the dashboard and the FAQ service run on Vercel. The dashboard is a static site, so it needs no build.

1. In Vercel, choose Add New, Project, and import `UmbrellaNET/FAQDashboard.github.io` from GitHub.
2. Set Framework Preset to Other. Leave the build command empty and the output directory as the project root.
3. Deploy. Every push to `main` redeploys production, and pull requests get preview deployments.
4. Optional: add a custom domain under Settings, Domains.

Then allow the site to sign users in:

1. Open the Firebase console for the project, then Authentication, Settings, Authorized domains.
2. Add the dashboard's Vercel domain, any custom domain, and `localhost` for local testing. Preview deployments use different addresses, so add them only if you need to sign in on previews.
3. Under Authentication, Sign-in method, enable Email/Password and Google.

Notes:

- The repository name ends in `.github.io` because it was set up for GitHub Pages. That name has no effect on Vercel. You can rename the repository if you like, then reconnect it in Vercel.
- A deployed Vercel site is public. Anyone can read every file in it. Vercel environment variables are not available to plain HTML pages, so secrets must live in the FAQ service, not here.
- The FAQ service must allow the dashboard's Vercel address in its CORS settings.

## Getting started

### Prerequisites

- A modern web browser
- Git
- Access to the Firebase project `umbrellalabs-faq`
- Access to the Upstash Redis database used by the FAQ service
- Optional: Python 3 to run a local web server

### 1. Clone

```bash
git clone https://github.com/UmbrellaNET/FAQDashboard.github.io.git
cd FAQDashboard.github.io
```

### 2. Configure

Set the Firebase web configuration in `index.html`. Do not put a database token in any page. See [Security and data protection](#security-and-data-protection) for how data access should be set up.

### 3. Run locally

Serve the folder rather than opening the file directly, because Firebase sign-in needs a web address:

```bash
python3 -m http.server 8000
```

Then open http://localhost:8000 and sign in. `localhost` must be in the Firebase authorized domains.

### 4. Deploy

Commit and push to `main`. Vercel deploys it. Or use the Vercel CLI:

```bash
npm i -g vercel
vercel --prod
```

## Configuration reference

| Setting | Where | Purpose |
| --- | --- | --- |
| Firebase web config | `<script>` in `index.html` | Connects sign-in to the Firebase project. The Firebase web API key is designed to be public |
| Authorized domains and sign-in methods | Firebase console, Authentication | Sites and methods allowed to sign users in |
| Post-login page | `index.html`, `window.location.href = 'index2.html'` | Where users land after signing in |
| Data source address | `index2.html`, `chats.html`, `analytics.html`, `agent.html` | Where conversations and missed requests are read from. [Replace with the FAQ API address once the fix below is made] |
| Message set-up count | `BOOTSTRAP` / `BOOTSTRAP_SKIP` constant (2) | Number of set-up items at the start of each stored conversation to hide |
| Refresh intervals | Each page | Badge 15 to 60 seconds, analytics 10 minutes, agent heartbeat 8 seconds |
| Google Maps key | `index2.html` | Loads the Maps script. Restrict the key to this site's address |

Never put a database token, service account key or any other secret in this repository.

## Repository layout

```
index.html               Sign-in page
index2.html              Dashboard home
register.html            Create an account
forgot-password.html     Password reset
chats.html               Saved conversations
analytics.html           Usage analytics
agent.html               Live agent panel
missed.html              Missed agent requests
profile.html             Profile
css/                     Template styles
js/                      Template scripts
img/                     Logo and images
src/plugins/             Template plugins and icon fonts
favicon.ico              Site icon
README.md                This file
```

[Adjust this list to match the real files.]

## Testing and verification

Before pushing a change:

1. Serve the site locally and sign in with an email account and with Google.
2. Try a wrong password and an unknown email, and confirm the messages are clear.
3. Open every dashboard page directly while signed out, and confirm no private data appears.
4. Open Chats and check that sessions load, messages show in the right order and dates, and Find Session works.
5. Open Analytics, change the date range and confirm the cards and chart update. Check the warning appears for messages with no timestamp.
6. Test live chat with the visitor widget and the agent panel on the real site addresses, in two different browsers, not two tabs of one browser.
7. Trigger a missed agent request and confirm the badge updates.
8. Check the pages at phone width and at desktop width, and look for errors in the browser console.
9. After pushing, hard refresh the live site, because browsers cache files.

**Live chat cannot work as built across real users.** The browser broadcast channel only connects pages of the same site address in the same browser on the same computer. A visitor on the website and an agent on this dashboard are on different addresses and different computers, so requests, messages and the online status will not reach each other. Replace it with a server-based channel, such as WebSockets, server-sent events or polling through the FAQ service backed by Redis, and send missed requests to the server instead of a browser channel.

**The agent panel has no authentication.** Anyone who opens `agent.html` can type a name, go online and accept chats. Require a Firebase sign-in, take the agent's identity from the verified token instead of a typed name, and check the agent role on the server.


## Troubleshooting

| Symptom | Likely cause and fix |
| --- | --- |
| Vercel shows 404 | `index.html` is not in the project root, or the output directory is set to a folder that does not exist. Check Settings, General in Vercel |
| Sign-in fails with a domain error | Add the site's Vercel domain (or custom domain) to Firebase, Authentication, Settings, Authorized domains |
| "This sign-in method is not enabled" | Enable Email/Password or Google under Authentication, Sign-in method |
| Google sign-in does nothing | The browser blocked the pop-up. Allow pop-ups for the site |
| Chats says "No session found" or an error | The data call failed (check the console), the token is invalid or rotated, or there are no conversations with real messages |
| Analytics shows a timestamp warning | Stored messages have no `timestamp` field. Make the FAQ service save one with each message |
| Analytics chart is empty | No messages in the chosen date range. Widen the range |
| Badge stays hidden or shows 0 | The data call failed, or there are no unseen requests |
| Agent never receives requests | The widget and agent panel are on different sites or browsers, so the broadcast channel cannot connect them. See the security section |
| Desktop notifications do not appear | Permission was denied or dismissed. Allow notifications for the site in browser settings |
| A request for `js/` fails in the console | `index2.html` has an empty script tag (`<script src="js/">`). Remove it or give it a file name |
| Console warns about Google Maps | The key is restricted to other sites, or the `initMap` function is missing. Fix the key or remove the script |
| Changes do not appear | The deployment has not finished, or the browser cached old files. Check the Deployments tab in Vercel, then hard refresh |
| Analytics reports no sign-in traffic | The sign-in page uses an old Universal Analytics tag (`UA-...`), which Google stopped processing in 2023. Use the Google Analytics 4 ID from Firebase |

## Contributing

Issues and pull requests are welcome. Please:

- describe what you changed and how you tested it
- keep the interface simple and readable on phones
- never commit keys, tokens, exported conversations or personal data

For security issues, contact [security contact email] instead of opening a public issue.

## License

[Choose a license and add a `LICENSE` file. State it here.] The templates in `css/`, `js/` and `src/` have their own licenses, which must be kept.

Copyright (C) 2026 UmbrellaNET
