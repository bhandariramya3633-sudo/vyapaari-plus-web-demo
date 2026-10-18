import streamlit as st
import pandas as pd

st.set_page_config(page_title="Vyapaari+ | Business Console", page_icon="📊", layout="wide")

if "suppliers" not in st.session_state:
    st.session_state.suppliers = pd.DataFrame([
        {"Supplier ID":"SUP-001","Supplier":"ABC Traders","Invoice":25000.0,"Paid":15000.0,"Terms":"NET_30"},
        {"Supplier ID":"SUP-002","Supplier":"Sri Lakshmi Stores","Invoice":18000.0,"Paid":8000.0,"Terms":"NET_15"},
        {"Supplier ID":"SUP-003","Supplier":"National Distributors","Invoice":42000.0,"Paid":42000.0,"Terms":"NET_60"},
        {"Supplier ID":"SUP-004","Supplier":"Greenfield Supplies","Invoice":12000.0,"Paid":0.0,"Terms":"COD"},
    ])
if "orders" not in st.session_state:
    st.session_state.orders = pd.DataFrame([
        {"PO Number":"PO-1001","Supplier":"ABC Traders","Item":"Rice bags","Quantity":50,"Unit Price":850.0,"Status":"Received"},
        {"PO Number":"PO-1002","Supplier":"Sri Lakshmi Stores","Item":"Cooking oil","Quantity":30,"Unit Price":1450.0,"Status":"Pending"},
        {"PO Number":"PO-1003","Supplier":"Greenfield Supplies","Item":"Packaging boxes","Quantity":100,"Unit Price":25.0,"Status":"Pending"},
    ])
if "receipts" not in st.session_state:
    st.session_state.receipts = pd.DataFrame([
        {"PO Number":"PO-1001","Ordered Qty":50,"Received Qty":50,"Invoice Amount":42500.0,"Status":"Matched"},
        {"PO Number":"PO-1002","Ordered Qty":30,"Received Qty":25,"Invoice Amount":43500.0,"Status":"Review Required"},
    ])

st.markdown("""
<style>
.block-container {padding-top: 1.5rem; padding-bottom: 2rem;}
[data-testid="stMetric"] {background:var(--secondary-background-color);border:1px solid rgba(128,128,128,.2);padding:16px;border-radius:12px;}
[data-testid="stSidebar"] {border-right:1px solid rgba(128,128,128,.2);}
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("# 📊 Vyapaari+")
    st.caption("BUSINESS OPERATIONS CONSOLE")
    st.divider()
    page = st.radio("NAVIGATION", ["Executive Dashboard","Supplier Ledger","Purchase Orders","GRN & Invoice Matching","Reports & Exports"])
    st.divider()
    st.caption("Supplier Credit Accounting · Purchase Order Engine")
    st.caption("Demo mode · Sample data only")

suppliers = st.session_state.suppliers
orders = st.session_state.orders
receipts = st.session_state.receipts
suppliers["Balance"] = suppliers["Invoice"] - suppliers["Paid"]
orders["Order Total"] = orders["Quantity"] * orders["Unit Price"]

st.caption("VYAPAARI+ / CORE")
st.title(page)
st.caption("Supplier credit accounting, ledger reconciliation and purchase order management.")
st.info("Interactive demonstration using sample data. It is not connected to the production database.", icon="ℹ️")

if page == "Executive Dashboard":
    a,b,c,d = st.columns(4)
    a.metric("Total Invoices", f"₹{suppliers['Invoice'].sum():,.0f}")
    b.metric("Payments Made", f"₹{suppliers['Paid'].sum():,.0f}")
    c.metric("Outstanding", f"₹{suppliers['Balance'].sum():,.0f}")
    d.metric("Purchase Orders", f"₹{orders['Order Total'].sum():,.0f}")
    left,right = st.columns([1.5,1])
    with left:
        st.subheader("Payments vs outstanding")
        st.bar_chart(suppliers.set_index("Supplier")[["Paid","Balance"]])
    with right:
        st.subheader("Operations snapshot")
        st.write(f"**{len(suppliers)}** suppliers in demo")
        st.write(f"**{(suppliers['Balance'] > 0).sum()}** suppliers with balances")
        st.write(f"**{(orders['Status'] == 'Pending').sum()}** pending purchase orders")
        st.write(f"**{(receipts['Status'] != 'Matched').sum()}** receipt records needing review")
    st.subheader("Supplier balances")
    st.dataframe(suppliers[["Supplier ID","Supplier","Invoice","Paid","Balance"]], use_container_width=True, hide_index=True)

elif page == "Supplier Ledger":
    st.subheader("Supplier accounts and balances")
    search = st.text_input("Search supplier name or ID")
    filtered = suppliers[suppliers["Supplier"].str.contains(search, case=False, na=False) | suppliers["Supplier ID"].str.contains(search, case=False, na=False)]
    st.dataframe(filtered[["Supplier ID","Supplier","Terms","Invoice","Paid","Balance"]], use_container_width=True, hide_index=True)
    st.subheader("Record a demo payment")
    with st.form("payment_form"):
        sid = st.selectbox("Supplier", suppliers["Supplier ID"].tolist(), format_func=lambda x: suppliers.loc[suppliers["Supplier ID"] == x,"Supplier"].iloc[0])
        amount = st.number_input("Payment amount (₹)", min_value=1.0, value=500.0)
        submit = st.form_submit_button("Record demo payment")
    if submit:
        idx = suppliers.index[suppliers["Supplier ID"] == sid][0]
        balance = float(st.session_state.suppliers.loc[idx,"Invoice"] - st.session_state.suppliers.loc[idx,"Paid"])
        if amount > balance:
            st.error("Payment cannot exceed the outstanding balance.")
        else:
            st.session_state.suppliers.loc[idx,"Paid"] += amount
            st.success("Demo payment recorded for this session.")
            st.rerun()

elif page == "Purchase Orders":
    st.subheader("Purchase order register")
    st.metric("Total order value", f"₹{orders['Order Total'].sum():,.2f}")
    st.dataframe(orders, use_container_width=True, hide_index=True)
    st.subheader("Create a demo purchase order")
    with st.form("po_form"):
        supplier = st.selectbox("Supplier", suppliers["Supplier"].tolist())
        item = st.text_input("Item name", placeholder="e.g. Wheat flour")
        qty = st.number_input("Quantity", min_value=1, value=10)
        price = st.number_input("Unit price (₹)", min_value=0.0, value=100.0)
        create = st.form_submit_button("Create demo order")
    if create:
        if not item.strip():
            st.error("Please enter an item name.")
        else:
            num = 1001 + len(st.session_state.orders)
            new = {"PO Number":f"PO-{num}","Supplier":supplier,"Item":item.strip(),"Quantity":qty,"Unit Price":price,"Status":"Pending"}
            st.session_state.orders = pd.concat([st.session_state.orders,pd.DataFrame([new])],ignore_index=True)
            st.success(f"Created demo order PO-{num}.")
            st.rerun()

elif page == "GRN & Invoice Matching":
    st.subheader("Goods Receipt Note and invoice verification")
    st.write("Compare received quantities and invoice amounts with the purchase order.")
    st.dataframe(receipts, use_container_width=True, hide_index=True)
    with st.form("grn_form"):
        po = st.selectbox("Purchase order", orders["PO Number"].tolist())
        order = orders[orders["PO Number"] == po].iloc[0]
        qty_ordered = int(order["Quantity"])
        st.write(f"Ordered quantity: **{qty_ordered}**")
        qty_received = st.number_input("Quantity received", min_value=0, value=qty_ordered)
        invoice = st.number_input("Supplier invoice amount (₹)", min_value=0.0, value=float(order["Order Total"]))
        check = st.form_submit_button("Check matching")
    if check:
        qty_ok = qty_received == qty_ordered
        amount_ok = abs(invoice - float(order["Order Total"])) < 0.01
        if qty_ok and amount_ok:
            st.success("Quantity and invoice amount match the order.")
        else:
            st.warning("Discrepancy found. Review before approval.")
            if not qty_ok:
                st.write(f"Quantity difference: {qty_received - qty_ordered}")
            if not amount_ok:
                st.write(f"Invoice amount difference: ₹{invoice - float(order['Order Total']):,.2f}")

elif page == "Reports & Exports":
    st.subheader("Export business reports")
    kind = st.selectbox("Choose report", ["Supplier Ledger","Purchase Order Register","GRN Register"])
    report = suppliers.copy() if kind == "Supplier Ledger" else orders.copy() if kind == "Purchase Order Register" else receipts.copy()
    st.dataframe(report, use_container_width=True, hide_index=True)
    st.download_button("Download CSV report", data=report.to_csv(index=False).encode("utf-8"), file_name=kind.lower().replace(" ","_")+".csv", mime="text/csv", use_container_width=True)
    st.caption("Exports contain demonstration data, not live business records.")

st.divider()
st.caption("Vyapaari+ Core · Supplier credit accounting and purchase order demo")