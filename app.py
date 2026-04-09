import streamlit as st
import requests
import base64
import json

# ─────────────────────────────────────────────
#  CONFIG
# ─────────────────────────────────────────────
BASE_URL = "https://fastapi-library-management-zgqj.onrender.com"
TIMEOUT  = 60

st.set_page_config(
    page_title="LibraNet",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
#  CUSTOM CSS  – dark editorial theme
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@400;600;700&family=Syne:wght@400;500;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Syne', sans-serif;
    background-color: #0d0f14;
    color: #e8e3d9;
}
h1,h2,h3 { font-family:'Cormorant Garamond',serif; letter-spacing:.02em; }

section[data-testid="stSidebar"] {
    background: #111318 !important;
    border-right: 1px solid #2a2d38;
}
section[data-testid="stSidebar"] * { color: #c9c4b8 !important; }

.main .block-container { padding-top: 2rem; padding-bottom: 3rem; }

.page-banner {
    background: linear-gradient(135deg,#1a1d26 0%,#161920 100%);
    border-left: 4px solid #c9a84c;
    padding: 1rem 1.4rem;
    border-radius: 0 8px 8px 0;
    margin-bottom: 1.6rem;
}
.page-banner h2 { margin:0; font-size:1.8rem; color:#f0e8d0; }
.page-banner p  { margin:.2rem 0 0; font-size:.82rem; color:#7a7568; }

.stButton > button {
    background:#c9a84c !important;
    color:#0d0f14 !important;
    border:none !important;
    border-radius:6px !important;
    font-family:'Syne',sans-serif !important;
    font-weight:700 !important;
    font-size:.82rem !important;
    letter-spacing:.06em !important;
    padding:.45rem 1.2rem !important;
}
.stButton > button:hover { opacity:.85 !important; }

.stTextInput input, .stNumberInput input {
    background:#1a1d26 !important;
    border:1px solid #2a2d38 !important;
    color:#e8e3d9 !important;
    border-radius:6px !important;
}

.stTabs [data-baseweb="tab-list"] { border-bottom:1px solid #2a2d38; gap:.5rem; }
.stTabs [data-baseweb="tab"] {
    background:transparent !important;
    color:#7a7568 !important;
    border:none !important;
    font-family:'Syne',sans-serif;
    font-size:.8rem;
    letter-spacing:.06em;
    padding:.4rem .8rem;
}
.stTabs [aria-selected="true"] {
    color:#c9a84c !important;
    border-bottom:2px solid #c9a84c !important;
}

hr { border-color:#22252f !important; }

.token-box {
    background:#0a0c12;
    color:#4a4e5a;
    padding:8px 10px;
    border-radius:6px;
    font-size:11px;
    word-break:break-all;
    font-family:monospace;
}
.role-chip {
    display:inline-block;
    margin-top:4px;
    padding:3px 12px;
    border-radius:4px;
    font-size:.75rem;
    font-weight:700;
    letter-spacing:.08em;
    text-transform:uppercase;
}
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
#  SESSION STATE
# ─────────────────────────────────────────────
for key, default in [
    ("token",        None),
    ("role",         None),
    ("user_name",    None),
    ("user_id",      None),
    ("server_awake", False),
]:
    if key not in st.session_state:
        st.session_state[key] = default


# ─────────────────────────────────────────────
#  HELPERS
# ─────────────────────────────────────────────
def auth_headers():
    return {"Authorization": f"Bearer {st.session_state.token}"}


def decode_jwt_role(token: str) -> str:
    """Decode role directly from JWT payload — no extra API call needed."""
    try:
        # JWT = header.payload.signature — payload is base64url encoded
        payload_b64 = token.split(".")[1]
        # Fix padding
        payload_b64 += "=" * (4 - len(payload_b64) % 4)
        payload = json.loads(base64.urlsafe_b64decode(payload_b64))
        return payload.get("role", "user")
    except Exception:
        return "user"

def is_admin():
    return st.session_state.role in ("admin", "super_admin")

def is_super_admin():
    return st.session_state.role == "super_admin"


def api(method, path, **kwargs):
    kwargs.setdefault("timeout", TIMEOUT)
    kwargs.setdefault("headers", auth_headers())
    try:
        r = getattr(requests, method)(f"{BASE_URL}{path}", **kwargs)
        return r
    except requests.exceptions.ReadTimeout:
        st.error("⏱️ Request timed out — server may be waking up. Please retry.")
        st.session_state.server_awake = False
        return None
    except Exception as e:
        st.error(f"Connection error: {e}")
        return None


def show(r, ok_msg=None):
    if r is None:
        return
    if r.status_code in (200, 201):
        if ok_msg:
            st.success(f"✅ {ok_msg}")
        try:
            data = r.json()
            if isinstance(data, list):
                if data and isinstance(data[0], dict):
                    st.dataframe(data, use_container_width=True)
                else:
                    st.json(data)
            elif isinstance(data, dict):
                items = list(data.items())
                if 1 < len(items) <= 5:
                    cols = st.columns(len(items))
                    for i, (k, v) in enumerate(items):
                        with cols[i]:
                            st.metric(str(k).replace("_", " ").title(), str(v))
                else:
                    st.json(data)
            else:
                st.write(data)
        except Exception:
            st.write(r.text)
    else:
        st.error(f"❌ Error {r.status_code}")
        try:
            st.json(r.json())
        except Exception:
            st.write(r.text)


def banner(title, subtitle=""):
    st.markdown(f"""
    <div class="page-banner">
        <h2>{title}</h2>
        {'<p>' + subtitle + '</p>' if subtitle else ''}
    </div>""", unsafe_allow_html=True)


def section(title):
    st.markdown(
        f"<h4 style='color:#c9a84c;margin-top:1.2rem;margin-bottom:.2rem;'>{title}</h4>",
        unsafe_allow_html=True,
    )
    st.markdown("<hr style='margin:.1rem 0 .6rem;'>", unsafe_allow_html=True)


# ─────────────────────────────────────────────
#  AUTH PAGE
# ─────────────────────────────────────────────
def page_auth():
    _, col, _ = st.columns([1, 2, 1])
    with col:
        st.markdown("""
        <div style='text-align:center;padding:2rem 0 1rem;'>
            <div style='font-size:3rem;'>📚</div>
            <h1 style='font-family:"Cormorant Garamond",serif;font-size:2.6rem;
                       color:#f0e8d0;margin:.2rem 0 .1rem;'>LibraNet</h1>
            <p style='color:#5a5650;font-size:.82rem;letter-spacing:.12em;
                      text-transform:uppercase;'>Online Library Management</p>
        </div>""", unsafe_allow_html=True)

        if not st.session_state.server_awake:
            st.info("⏳ The backend runs on a free Render server that sleeps on inactivity. "
                    "**First login may take up to 60 s** while it wakes — please be patient.")

        tab_login, tab_register = st.tabs(["🔐  Login", "📝  Register"])

        # ── LOGIN ──────────────────────────────────
        with tab_login:
            st.markdown("<br>", unsafe_allow_html=True)
            email    = st.text_input("Email", placeholder="you@example.com", key="li_email")
            password = st.text_input("Password", type="password", key="li_pass")
            st.markdown("<br>", unsafe_allow_html=True)

            if st.button("Login", use_container_width=True, key="li_btn"):
                if not email or not password:
                    st.warning("Please fill in both fields.")
                else:
                    with st.spinner("Logging in… server may be waking up, please wait."):
                        try:
                            r = requests.post(
                                f"{BASE_URL}/auth/login",
                                json={"email": email, "password": password},
                                timeout=TIMEOUT,
                            )
                        except requests.exceptions.ReadTimeout:
                            st.error("⏱️ Timed out. Please try again in ~30 seconds.")
                            r = None

                    if r is not None and r.status_code == 200:
                        st.session_state.token = r.json().get("access_token")
                        st.session_state.server_awake = True
                        # Decode role from JWT directly (UserResponse schema lacks role field)
                        st.session_state.role = decode_jwt_role(st.session_state.token)
                        # Fetch name/id from profile
                        me = requests.get(
                            f"{BASE_URL}/user/user/me",
                            headers=auth_headers(),
                            timeout=15,
                        )
                        if me.status_code == 200:
                            u = me.json()
                            st.session_state.user_name = u.get("name", "")
                            st.session_state.user_id   = u.get("id")
                        st.success(f"Logged in as {st.session_state.role.replace('_', ' ').title()}!")
                        st.rerun()
                    elif r is not None:
                        st.error(f"Login failed ({r.status_code})")
                        try:   st.json(r.json())
                        except: st.write(r.text)

        # ── REGISTER ───────────────────────────────
        with tab_register:
            st.markdown("<br>", unsafe_allow_html=True)
            c1, c2 = st.columns(2)
            with c1:
                rg_name  = st.text_input("Full Name",    key="rg_name")
                rg_email = st.text_input("Email",        key="rg_email")
                rg_cc    = st.text_input("Country Code", placeholder="+91", key="rg_cc")
            with c2:
                rg_phone = st.text_input("Phone", placeholder="9876543210", key="rg_phone")
                rg_pass  = st.text_input("Password (min 6 chars)", type="password", key="rg_pass")

            st.caption("ℹ️ The very **first** registered account automatically becomes **Super Admin**. All others start as regular users.")
            st.markdown("<br>", unsafe_allow_html=True)

            if st.button("Create Account", use_container_width=True, key="rg_btn"):
                if not all([rg_name, rg_email, rg_cc, rg_phone, rg_pass]):
                    st.warning("All fields are required.")
                else:
                    with st.spinner("Registering…"):
                        r = requests.post(
                            f"{BASE_URL}/auth/register",
                            json={
                                "name":         rg_name,
                                "email":        rg_email,
                                "country_code": rg_cc,
                                "phone":        rg_phone,
                                "password":     rg_pass,
                            },
                            timeout=TIMEOUT,
                        )
                    show(r, "Account created! Please log in.")


# ─────────────────────────────────────────────
#  BOOKS PAGE
# ─────────────────────────────────────────────
def page_books():
    banner("📖 Books", "Browse, search, and manage the library catalogue")

    tab_labels = ["📋 All Books", "🔍 Search", "🔎 By ID"]
    if is_admin():
        tab_labels += ["➕ Add", "✏️ Update", "🗑️ Delete"]

    tabs = st.tabs(tab_labels)

    # ── ALL BOOKS ──
    with tabs[0]:
        section("All Books")
        if st.button("Fetch All Books", key="bk_all"):
            show(api("get", "/books/"))

    # ── SEARCH ──
    with tabs[1]:
        section("Search by Title")
        name = st.text_input("Title (partial match OK)", key="bk_sname")
        if st.button("Search", key="bk_sbtn"):
            if name:
                show(api("get", "/books/search/", params={"name": name}))
            else:
                st.warning("Enter a search term.")

    # ── BY ID ──
    with tabs[2]:
        section("Get Book by ID")
        bid = st.number_input("Book ID", min_value=1, value=1, key="bk_bid")
        if st.button("Fetch Book", key="bk_bidbtn"):
            show(api("get", f"/books/{bid}"))

    if is_admin():
        # ── ADD ──
        with tabs[3]:
            section("Add New Book  ·  Admin Only")
            c1, c2 = st.columns(2)
            with c1:
                a_title    = st.text_input("Title",    key="bk_a_title")
                a_author   = st.text_input("Author",   key="bk_a_author")
                a_category = st.text_input("Category", key="bk_a_cat")
            with c2:
                a_isbn    = st.text_input("ISBN",    key="bk_a_isbn")
                a_pdf_url = st.text_input("PDF URL", key="bk_a_pdf")
            if st.button("Add Book", key="bk_addbtn"):
                if all([a_title, a_author, a_category, a_isbn, a_pdf_url]):
                    show(api("post", "/books/", json={
                        "title": a_title, "author": a_author,
                        "category": a_category, "isbn": a_isbn, "pdf_url": a_pdf_url,
                    }), "Book added!")
                else:
                    st.warning("All fields are required.")

        # ── UPDATE ──
        with tabs[4]:
            section("Update Book  ·  Admin Only")
            st.caption("⚠️ This endpoint replaces ALL fields — fill every box.")
            u_id = st.number_input("Book ID to update", min_value=1, value=1, key="bk_uid")
            c1, c2 = st.columns(2)
            with c1:
                u_title    = st.text_input("Title",    key="bk_u_title")
                u_author   = st.text_input("Author",   key="bk_u_author")
                u_category = st.text_input("Category", key="bk_u_cat")
            with c2:
                u_isbn    = st.text_input("ISBN",    key="bk_u_isbn")
                u_pdf_url = st.text_input("PDF URL", key="bk_u_pdf")
            if st.button("Update Book", key="bk_updbtn"):
                if all([u_title, u_author, u_category, u_isbn, u_pdf_url]):
                    show(api("put", f"/books/{u_id}", json={
                        "title": u_title, "author": u_author,
                        "category": u_category, "isbn": u_isbn, "pdf_url": u_pdf_url,
                    }), "Book updated!")
                else:
                    st.warning("All fields are required.")

        # ── DELETE ──
        with tabs[5]:
            section("Delete Book  ·  Admin Only")
            st.warning("⚠️ Books with active (issued) transactions cannot be deleted.")
            d_id = st.number_input("Book ID to delete", min_value=1, value=1, key="bk_did")
            if st.button("🗑️ Delete Book", key="bk_delbtn"):
                show(api("delete", f"/books/{d_id}"), "Book deleted.")


# ─────────────────────────────────────────────
#  TRANSACTIONS PAGE
# ─────────────────────────────────────────────
def page_transactions():
    banner("🔄 Transactions", "Issue, return, and read books")

    tab_labels = ["📤 Issue Book", "📥 Return Book", "📖 Read Book (PDF)"]
    if is_admin():
        tab_labels += ["📋 All Issued", "⏰ All Expired"]

    tabs = st.tabs(tab_labels)

    # ── ISSUE ──
    with tabs[0]:
        section("Issue a Book")
        st.info("Issues the book to **you** (logged-in user) for **7 days**.")
        iss_bid = st.number_input("Book ID to issue", min_value=1, value=1, key="tx_iss_bid")
        if st.button("Issue Book", key="tx_issbtn"):
            show(api("post", "/transactions/issue", json={"book_id": iss_bid}),
                 "Book issued! You have 7 days access.")

    # ── RETURN ──
    with tabs[1]:
        section("Return a Book")
        ret_bid = st.number_input("Book ID to return", min_value=1, value=1, key="tx_ret_bid")
        if st.button("Return Book", key="tx_retbtn"):
            show(api("post", f"/transactions/return/{ret_bid}"),
                 "Book returned successfully.")

    # ── READ / PDF ──
    with tabs[2]:
        section("Read Book PDF")
        st.info("Checks your active issue and returns the PDF link. You must have the book issued to access it.")
        read_bid = st.number_input("Book ID to read", min_value=1, value=1, key="tx_read_bid")
        if st.button("Get PDF Access", key="tx_readbtn"):
            r = api("get", f"/transactions/read/{read_bid}", allow_redirects=False)
            if r is not None:
                if r.status_code in (301, 302, 307, 308):
                    pdf_url = r.headers.get("location", "")
                    st.success("✅ Access granted!")
                    st.markdown(f"### [📄 Open PDF in new tab]({pdf_url})")
                    st.code(pdf_url, language=None)
                elif r.status_code == 200:
                    st.success("✅ Access granted!")
                    st.write(r.url)
                else:
                    show(r)

    if is_admin():
        # ── ISSUED (ADMIN) ──
        with tabs[3]:
            section("All Currently Issued Books  ·  Admin Only")
            if st.button("Fetch Issued", key="tx_adm_iss"):
                show(api("get", "/transactions/issued"))

        # ── EXPIRED (ADMIN) ──
        with tabs[4]:
            section("All Expired Transactions  ·  Admin Only")
            if st.button("Fetch Expired", key="tx_adm_exp"):
                show(api("get", "/transactions/expired"))


# ─────────────────────────────────────────────
#  USERS PAGE
# ─────────────────────────────────────────────
def page_users():
    banner("👥 Users", "Profile management and admin controls")

    tab_labels = ["👤 My Profile", "✏️ Edit Profile", "🔑 Change Password"]
    if is_admin():
        tab_labels += ["📋 All Users", "🔎 User by ID", "🗑️ Delete User"]
    if is_super_admin():
        tab_labels += ["⬆️ Promote to Admin", "👑 Transfer Super Admin"]

    tabs = st.tabs(tab_labels)

    # We build the full tab list upfront and index statically by position
    # Tabs 0,1,2 always exist; 3,4,5 for admin; 6,7 for super_admin

    # ── MY PROFILE (tab 0) ──
    with tabs[0]:
        section("My Profile")
        if st.button("Load My Profile", key="u_mebtn"):
            show(api("get", "/user/user/me"))

    # ── EDIT PROFILE (tab 1) ──
    with tabs[1]:
        section("Edit Profile")
        sub_name, sub_email, sub_phone = st.tabs(["📛 Name", "📧 Email", "📱 Phone"])

        with sub_name:
            new_name = st.text_input("New Name", key="u_new_name")
            if st.button("Update Name", key="u_namebtn"):
                if new_name:
                    show(api("put", "/user/user/me/name", json={"name": new_name}), "Name updated!")
                else:
                    st.warning("Enter a name.")

        with sub_email:
            new_email = st.text_input("New Email", key="u_new_email")
            if st.button("Update Email", key="u_emailbtn"):
                if new_email:
                    show(api("put", "/user/user/me/email", json={"email": new_email}), "Email updated!")
                else:
                    st.warning("Enter an email.")

        with sub_phone:
            c1, c2 = st.columns([1, 2])
            with c1:
                new_cc    = st.text_input("Country Code", placeholder="+91", key="u_new_cc")
            with c2:
                new_phone = st.text_input("Phone Number", key="u_new_phone")
            if st.button("Update Phone", key="u_phonebtn"):
                if new_cc and new_phone:
                    show(api("put", "/user/user/me/phone",
                             json={"country_code": new_cc, "phone": new_phone}),
                         "Phone updated!")
                else:
                    st.warning("Fill both fields.")

    # ── CHANGE PASSWORD (tab 2) ──
    with tabs[2]:
        section("Change Password")
        old_pw  = st.text_input("Current Password",           type="password", key="u_old_pw")
        new_pw  = st.text_input("New Password (min 6 chars)", type="password", key="u_new_pw")
        new_pw2 = st.text_input("Confirm New Password",       type="password", key="u_new_pw2")
        if st.button("Change Password", key="u_pwbtn"):
            if not old_pw or not new_pw:
                st.warning("Fill all fields.")
            elif new_pw != new_pw2:
                st.error("New passwords do not match.")
            elif len(new_pw) < 6:
                st.error("Password must be at least 6 characters.")
            else:
                show(api("put", "/user/user/me/password",
                         json={"old_password": old_pw, "new_password": new_pw}),
                     "Password changed successfully!")

    if is_admin():
        # ── ALL USERS (tab 3) ──
        with tabs[3]:
            section("All Users  ·  Admin Only")
            if st.button("Fetch All Users", key="u_allbtn"):
                show(api("get", "/user/user/"))

        # ── USER BY ID (tab 4) ──
        with tabs[4]:
            section("Get User by ID  ·  Admin Only")
            uid = st.number_input("User ID", min_value=1, value=1, key="u_byid")
            if st.button("Fetch User", key="u_byidbtn"):
                show(api("get", f"/user/user/{uid}"))

        # ── DELETE USER (tab 5) ──
        with tabs[5]:
            section("Delete User  ·  Admin Only")
            st.warning("⚠️ Cannot delete: Super Admin, yourself, or users with active borrowed books.")
            del_uid = st.number_input("User ID to delete", min_value=1, value=1, key="u_delid")
            if st.button("🗑️ Delete User", key="u_delbtn"):
                show(api("delete", f"/user/user/{del_uid}"), "User deleted.")

    if is_super_admin():
        # ── PROMOTE TO ADMIN (tab 6) ──
        with tabs[6]:
            section("Promote User to Admin  ·  Super Admin Only")
            promo_uid = st.number_input("User ID to promote", min_value=1, value=1, key="u_promoid")
            if st.button("⬆️ Make Admin", key="u_promobtn"):
                show(api("put", f"/user/user/make-admin/{promo_uid}"),
                     "User promoted to Admin!")

        # ── TRANSFER SUPER ADMIN (tab 7) ──
        with tabs[7]:
            section("Transfer Super Admin  ·  Super Admin Only")
            st.error("⚠️ This permanently removes YOUR Super Admin status and grants it to another user.")
            trans_uid = st.number_input("Target User ID", min_value=1, value=1, key="u_transid")
            confirmed = st.checkbox("I understand this action cannot be undone", key="u_confirm")
            if st.button("👑 Transfer Super Admin", key="u_transbtn"):
                if confirmed:
                    show(api("put", f"/user/user/transfer-super-admin/{trans_uid}"),
                         "Super Admin role transferred.")
                else:
                    st.warning("Check the confirmation box first.")


# ─────────────────────────────────────────────
#  ANALYTICS PAGE
# ─────────────────────────────────────────────
def page_analytics():
    banner("📊 Analytics", "Library statistics and insights")

    # ── PUBLIC ──
    section("📚 Available to All Users")
    if st.button("Get Total Books", key="an_totbooks"):
        show(api("get", "/analytics/total-books"))

    if is_admin():
        st.markdown("<br>", unsafe_allow_html=True)
        section("🔒 Admin-Only Analytics")
        c1, c2 = st.columns(2)

        with c1:
            st.markdown("**👥 Total Registered Users**")
            if st.button("Get Total Users", key="an_totusers"):
                show(api("get", "/analytics/total-users"))

            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("**🔥 Most Borrowed Books**")
            if st.button("Get Most Borrowed", key="an_mostborrow"):
                show(api("get", "/analytics/most-borrowed"))

        with c2:
            st.markdown("**📋 Currently Issued Books**")
            if st.button("Get Issued Books", key="an_issued"):
                show(api("get", "/analytics/issued"))


# ─────────────────────────────────────────────
#  SIDEBAR
# ─────────────────────────────────────────────
def sidebar():
    with st.sidebar:
        st.markdown("""
        <div style='padding:.6rem 0 1rem;'>
            <span style='font-size:1.6rem;'>📚</span>
            <span style='font-family:"Cormorant Garamond",serif;font-size:1.5rem;
                         color:#f0e8d0;margin-left:.5rem;'>LibraNet</span>
        </div>""", unsafe_allow_html=True)

        role  = st.session_state.role or "user"
        rclr  = {"super_admin": "#c9a84c", "admin": "#4caf7d", "user": "#4c8ec9"}.get(role, "#7a7a8a")
        name  = st.session_state.user_name or "User"
        st.markdown(f"""
        <div style='margin-bottom:1rem;'>
            <div style='color:#c9c4b8;font-size:.92rem;font-weight:600;'>{name}</div>
            <span class='role-chip' style='background:{rclr}22;color:{rclr};'>
                {role.replace("_", " ")}
            </span>
        </div>""", unsafe_allow_html=True)

        st.markdown("---")

        page = st.radio(
            "nav",
            ["📖 Books", "🔄 Transactions", "👥 Users", "📊 Analytics"],
            label_visibility="collapsed",
        )

        st.markdown("---")

        if st.button("🚪 Logout", use_container_width=True, key="sb_logout"):
            for k in ("token", "role", "user_name", "user_id"):
                st.session_state[k] = None
            st.session_state.server_awake = False
            st.rerun()

        with st.expander("🔑 Debug Token"):
            tok = st.session_state.token or ""
            st.markdown(
                f'<div class="token-box">{tok[:60]}{"…" if len(tok) > 60 else ""}</div>',
                unsafe_allow_html=True,
            )

    return page


# ─────────────────────────────────────────────
#  MAIN
# ─────────────────────────────────────────────
def main():
    if not st.session_state.token:
        page_auth()
        return

    page = sidebar()

    if   page == "📖 Books":        page_books()
    elif page == "🔄 Transactions": page_transactions()
    elif page == "👥 Users":        page_users()
    elif page == "📊 Analytics":    page_analytics()


if __name__ == "__main__":
    main()