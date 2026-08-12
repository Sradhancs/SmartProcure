import streamlit as st
import pandas as pd
import numpy as np
import os
import sys
from datetime import datetime

# ============================================================
# SMARTPROCURE
# PHASE 18 - STREAMLIT PROCUREMENT DASHBOARD
# ============================================================

st.set_page_config(
    page_title="SmartProcure Dashboard",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# DATABASE IMPORT
# ============================================================

# database.py is located in:
# C:\SmartProcure\python\database.py

PYTHON_FOLDER = r"C:\SmartProcure\python"

if PYTHON_FOLDER not in sys.path:
    sys.path.append(PYTHON_FOLDER)

try:
    from database import engine
    DATABASE_CONNECTED = True
except Exception as e:
    DATABASE_CONNECTED = False
    DATABASE_ERROR = str(e)


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown(
    """
    <style>

    .main-title {
        font-size: 38px;
        font-weight: 700;
        margin-bottom: 0px;
    }

    .sub-title {
        font-size: 18px;
        color: #666666;
        margin-top: 0px;
        margin-bottom: 25px;
    }

    .section-title {
        font-size: 25px;
        font-weight: 650;
        margin-top: 20px;
        margin-bottom: 10px;
    }

    div[data-testid="stMetric"] {
        border: 1px solid #dddddd;
        border-radius: 10px;
        padding: 12px;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# HEADER
# ============================================================

st.markdown(
    '<div class="main-title">📦 SmartProcure</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="sub-title">'
    'Predictive Procurement & Inventory Management Dashboard'
    '</div>',
    unsafe_allow_html=True
)


# ============================================================
# DATABASE CONNECTION CHECK
# ============================================================

if not DATABASE_CONNECTED:

    st.error(
        "Unable to connect to the SmartProcure database."
    )

    st.code(DATABASE_ERROR)

    st.stop()


# ============================================================
# HELPER FUNCTION
# ============================================================

@st.cache_data(ttl=60)
def load_query(query):

    try:
        return pd.read_sql(query, engine)

    except Exception as e:

        st.error(
            f"Database query failed:\n\n{e}"
        )

        return pd.DataFrame()


# ============================================================
# LOAD MATERIALS
# ============================================================

materials = load_query(
    """
    SELECT
        materialid,
        materialcode,
        materialname,
        category,
        unit,
        unitcost,
        minimumstock,
        maximumstock
    FROM materials
    ORDER BY materialid
    """
)


# ============================================================
# LOAD INVENTORY
# ============================================================

inventory = load_query(
    """
    SELECT
        inventoryid,
        materialid,
        inventorydate,
        openingstock,
        receivedquantity,
        consumedquantity,
        closingstock
    FROM inventory
    ORDER BY inventorydate
    """
)


# ============================================================
# LOAD PREDICTIONS
# ============================================================

predictions = load_query(
    """
    SELECT
        predictionid,
        materialid,
        predictiondate,
        forecastquantity,
        stockoutprobability,
        recommendedpurchase
    FROM predictions
    ORDER BY predictiondate
    """
)


# ============================================================
# LOAD STOCKOUT RISK
# ============================================================

stockout_risk = load_query(
    """
    SELECT
        stockoutriskid,
        materialid,
        forecastdate,
        forecastquantity,
        currentstock,
        projectedstockafterdemand,
        minimumstock,
        risklevel,
        shortagequantity,
        shortagevalue
    FROM stockoutrisk
    ORDER BY forecastdate
    """
)


# ============================================================
# LOAD PROCUREMENT RECOMMENDATIONS
# ============================================================

procurement = load_query(
    """
    SELECT
        recommendationid,
        materialid,
        recommendationdate,
        forecastquantity,
        openingstock,
        minimumstock,
        maximumstock,
        recommendedpurchase,
        projectedclosingstock,
        unitcost,
        estimatedpurchasecost,
        risklevel,
        procurementpriority,
        recommendationreason,
        createdat
    FROM procurementrecommendations
    ORDER BY recommendationid
    """
)


# ============================================================
# LOAD SUPPLIERS
# ============================================================

suppliers = load_query(
    """
    SELECT
        supplierid,
        suppliercode,
        suppliername,
        location,
        averageleadtime,
        rating,
        createdat
    FROM suppliers
    ORDER BY supplierid
    """
)


# ============================================================
# LOAD SUPPLIER RECOMMENDATIONS
# ============================================================

supplier_recommendations = load_query(
    """
    SELECT
        supplierrecommendationid,
        recommendationid,
        materialid,
        supplierid,
        recommendationdate,
        requiredquantity,
        supplierrating,
        averageleadtime,
        ratingscore,
        leadtimescore,
        supplierscore,
        supplierrank,
        recommendedsupplier,
        selectionreason,
        createdat
    FROM supplierrecommendations
    ORDER BY recommendationid, supplierrank
    """
)


# ============================================================
# LOAD PURCHASE ORDER RECOMMENDATIONS
# ============================================================

po_recommendations = load_query(
    """
    SELECT
        porecommendationid,
        recommendationid,
        supplierrecommendationid,
        materialid,
        supplierid,
        recommendationdate,
        requiredquantity,
        unitcost,
        estimatedtotalcost,
        supplierleadtime,
        requiredbydate,
        procurementpriority,
        risklevel,
        approvalstatus,
        approvedby,
        approvaldate,
        postatus,
        recommendationreason,
        createdat
    FROM purchaseorderrecommendations
    ORDER BY porecommendationid
    """
)


# ============================================================
# LOAD PURCHASE ORDERS
# ============================================================

purchase_orders = load_query(
    """
    SELECT
        poid,
        ponumber,
        supplierid,
        podate,
        expecteddeliverydate,
        actualdeliverydate,
        status
    FROM purchaseorders
    ORDER BY poid
    """
)


# ============================================================
# LOAD PURCHASE ORDER ITEMS
# ============================================================

po_items = load_query(
    """
    SELECT
        poitemid,
        poid,
        materialid,
        quantity,
        unitprice
    FROM purchaseorderitems
    ORDER BY poitemid
    """
)


# ============================================================
# CHECK DATA
# ============================================================

if materials.empty and procurement.empty and purchase_orders.empty:

    st.warning(
        "No SmartProcure data was found in the database."
    )

    st.info(
        "Run Phases 14–17 before opening the dashboard."
    )

    st.stop()


# ============================================================
# DATE CONVERSIONS
# ============================================================

date_columns = {
    "inventory": ["inventorydate"],
    "predictions": ["predictiondate"],
    "stockout_risk": ["forecastdate"],
    "procurement": ["recommendationdate", "createdat"],
    "supplier_recommendations": [
        "recommendationdate",
        "createdat"
    ],
    "po_recommendations": [
        "recommendationdate",
        "requiredbydate",
        "approvaldate",
        "createdat"
    ],
    "purchase_orders": [
        "podate",
        "expecteddeliverydate",
        "actualdeliverydate"
    ]
}

for df_name, columns in date_columns.items():

    df = globals().get(df_name)

    if df is not None and not df.empty:

        for column in columns:

            if column in df.columns:

                df[column] = pd.to_datetime(
                    df[column],
                    errors="coerce"
                )


# ============================================================
# NUMERIC CONVERSIONS
# ============================================================

numeric_dataframes = [
    materials,
    inventory,
    predictions,
    stockout_risk,
    procurement,
    supplier_recommendations,
    po_recommendations,
    po_items
]

for df in numeric_dataframes:

    if not df.empty:

        for column in df.columns:

            if column not in [
                "materialcode",
                "materialname",
                "category",
                "unit",
                "risklevel",
                "procurementpriority",
                "recommendationreason",
                "suppliercode",
                "suppliername",
                "location",
                "recommendedsupplier",
                "selectionreason",
                "approvalstatus",
                "approvedby",
                "postatus"
            ]:

                if df[column].dtype == "object":

                    try:

                        df[column] = pd.to_numeric(
                            df[column],
                            errors="ignore"
                        )

                    except Exception:
                        pass


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.title("📊 SmartProcure")

st.sidebar.markdown(
    "### Dashboard Navigation"
)

page = st.sidebar.radio(
    "Select Dashboard",
    [
        "Executive Dashboard",
        "Procurement Recommendations",
        "Supplier Analysis",
        "Purchase Orders",
        "Approval Tracking",
        "Delivery Tracking",
        "Risk Analysis",
        "Forecast Analysis",
        "Data Explorer"
    ]
)

st.sidebar.markdown("---")

st.sidebar.info(
    "SmartProcure Phase 18\n\n"
    "Predictive Procurement Dashboard"
)

if st.sidebar.button("🔄 Refresh Data"):

    st.cache_data.clear()
    st.rerun()


# ============================================================
# EXECUTIVE DASHBOARD
# ============================================================

if page == "Executive Dashboard":

    st.markdown(
        '<div class="section-title">'
        '📊 Executive Dashboard'
        '</div>',
        unsafe_allow_html=True
    )

    # --------------------------------------------------------
    # KPI CALCULATIONS
    # --------------------------------------------------------

    total_materials = len(materials)

    total_recommendations = len(procurement)

    urgent_count = 0
    high_count = 0
    medium_count = 0
    low_count = 0

    if not procurement.empty:

        urgent_count = (
            procurement["procurementpriority"]
            .astype(str)
            .str.upper()
            .eq("URGENT")
            .sum()
        )

        high_count = (
            procurement["procurementpriority"]
            .astype(str)
            .str.upper()
            .eq("HIGH")
            .sum()
        )

        medium_count = (
            procurement["procurementpriority"]
            .astype(str)
            .str.upper()
            .eq("MEDIUM")
            .sum()
        )

        low_count = (
            procurement["procurementpriority"]
            .astype(str)
            .str.upper()
            .eq("LOW")
            .sum()
        )

    total_procurement_value = 0

    if not procurement.empty:

        total_procurement_value = pd.to_numeric(
            procurement["estimatedpurchasecost"],
            errors="coerce"
        ).fillna(0).sum()

    total_purchase_order_value = 0

    if not po_items.empty:

        po_items["totalvalue"] = (
            pd.to_numeric(
                po_items["quantity"],
                errors="coerce"
            ).fillna(0)
            *
            pd.to_numeric(
                po_items["unitprice"],
                errors="coerce"
            ).fillna(0)
        )

        total_purchase_order_value = (
            po_items["totalvalue"].sum()
        )

    pending_approvals = 0

    if not po_recommendations.empty:

        pending_approvals = (
            po_recommendations["approvalstatus"]
            .astype(str)
            .str.upper()
            .eq("PENDING")
            .sum()
        )

    pending_deliveries = 0

    if not purchase_orders.empty:

        pending_deliveries = (
            purchase_orders["actualdeliverydate"]
            .isna()
            .sum()
        )

    # --------------------------------------------------------
    # KPI ROW 1
    # --------------------------------------------------------

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Materials",
        total_materials
    )

    col2.metric(
        "Procurement Recommendations",
        total_recommendations
    )

    col3.metric(
        "Urgent",
        urgent_count
    )

    col4.metric(
        "High Priority",
        high_count
    )

    # --------------------------------------------------------
    # KPI ROW 2
    # --------------------------------------------------------

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Medium Priority",
        medium_count
    )

    col2.metric(
        "Low Priority",
        low_count
    )

    col3.metric(
        "Pending Approvals",
        pending_approvals
    )

    col4.metric(
        "Pending Deliveries",
        pending_deliveries
    )

    # --------------------------------------------------------
    # FINANCIAL KPI
    # --------------------------------------------------------

    st.markdown("### 💰 Procurement Financial Summary")

    col1, col2 = st.columns(2)

    col1.metric(
        "Recommended Procurement Value",
        f"₹{total_procurement_value:,.2f}"
    )

    col2.metric(
        "Purchase Order Value",
        f"₹{total_purchase_order_value:,.2f}"
    )

    # --------------------------------------------------------
    # PRIORITY DISTRIBUTION
    # --------------------------------------------------------

    st.markdown("### 📌 Procurement Priority")

    priority_data = pd.DataFrame(
        {
            "Priority": [
                "URGENT",
                "HIGH",
                "MEDIUM",
                "LOW"
            ],
            "Count": [
                urgent_count,
                high_count,
                medium_count,
                low_count
            ]
        }
    )

    col1, col2 = st.columns(2)

    with col1:

        st.bar_chart(
            priority_data.set_index("Priority")
        )

    with col2:

        st.dataframe(
            priority_data,
            use_container_width=True,
            hide_index=True
        )

    # --------------------------------------------------------
    # TOP PROCUREMENT ITEMS
    # --------------------------------------------------------

    st.markdown("### 🛒 Recommended Procurement")

    if not procurement.empty:

        top_procurement = procurement.copy()

        if "materialid" in top_procurement.columns:

            top_procurement = top_procurement.merge(
                materials[
                    [
                        "materialid",
                        "materialcode",
                        "materialname"
                    ]
                ],
                on="materialid",
                how="left"
            )

        columns = [
            "materialcode",
            "materialname",
            "recommendedpurchase",
            "estimatedpurchasecost",
            "risklevel",
            "procurementpriority"
        ]

        columns = [
            c for c in columns
            if c in top_procurement.columns
        ]

        st.dataframe(
            top_procurement[columns],
            use_container_width=True,
            hide_index=True
        )


# ============================================================
# PROCUREMENT RECOMMENDATIONS
# ============================================================

elif page == "Procurement Recommendations":

    st.markdown(
        '<div class="section-title">'
        '🛒 Procurement Recommendations'
        '</div>',
        unsafe_allow_html=True
    )

    if procurement.empty:

        st.warning(
            "No procurement recommendations available."
        )

    else:

        procurement_display = procurement.copy()

        procurement_display = procurement_display.merge(
            materials[
                [
                    "materialid",
                    "materialcode",
                    "materialname",
                    "category",
                    "unit"
                ]
            ],
            on="materialid",
            how="left"
        )

        # ----------------------------------------------------
        # FILTER
        # ----------------------------------------------------

        col1, col2 = st.columns(2)

        priorities = [
            "ALL",
            "URGENT",
            "HIGH",
            "MEDIUM",
            "LOW"
        ]

        selected_priority = col1.selectbox(
            "Procurement Priority",
            priorities
        )

        risks = [
            "ALL",
            "CRITICAL",
            "HIGH",
            "MEDIUM",
            "LOW"
        ]

        selected_risk = col2.selectbox(
            "Risk Level",
            risks
        )

        filtered = procurement_display.copy()

        if selected_priority != "ALL":

            filtered = filtered[
                filtered["procurementpriority"]
                .astype(str)
                .str.upper()
                == selected_priority
            ]

        if selected_risk != "ALL":

            filtered = filtered[
                filtered["risklevel"]
                .astype(str)
                .str.upper()
                == selected_risk
            ]

        st.write(
            f"Showing **{len(filtered)}** recommendations"
        )

        display_columns = [
            "recommendationid",
            "materialcode",
            "materialname",
            "category",
            "recommendationdate",
            "forecastquantity",
            "openingstock",
            "minimumstock",
            "maximumstock",
            "projectedclosingstock",
            "recommendedpurchase",
            "unitcost",
            "estimatedpurchasecost",
            "risklevel",
            "procurementpriority",
            "recommendationreason"
        ]

        display_columns = [
            c for c in display_columns
            if c in filtered.columns
        ]

        st.dataframe(
            filtered[display_columns],
            use_container_width=True,
            hide_index=True
        )

        # ----------------------------------------------------
        # PURCHASE VALUE
        # ----------------------------------------------------

        total = pd.to_numeric(
            filtered["estimatedpurchasecost"],
            errors="coerce"
        ).fillna(0).sum()

        st.metric(
            "Filtered Procurement Value",
            f"₹{total:,.2f}"
        )


# ============================================================
# SUPPLIER ANALYSIS
# ============================================================

elif page == "Supplier Analysis":

    st.markdown(
        '<div class="section-title">'
        '🏭 Supplier Analysis'
        '</div>',
        unsafe_allow_html=True
    )

    if suppliers.empty:

        st.warning(
            "No supplier data available."
        )

    else:

        # ----------------------------------------------------
        # SUPPLIER RANKING
        # ----------------------------------------------------

        st.markdown("### 🏆 Supplier Ranking")

        if not supplier_recommendations.empty:

            supplier_ranking = (
                supplier_recommendations[
                    [
                        "supplierid",
                        "supplierrating",
                        "averageleadtime",
                        "ratingscore",
                        "leadtimescore",
                        "supplierscore",
                        "supplierrank"
                    ]
                ]
                .drop_duplicates("supplierid")
            )

            supplier_ranking = supplier_ranking.merge(
                suppliers,
                on="supplierid",
                how="left"
            )

            supplier_ranking = supplier_ranking.sort_values(
                "supplierrank"
            )

            display_columns = [
                "supplierrank",
                "suppliercode",
                "suppliername",
                "location",
                "supplierrating",
                "averageleadtime",
                "ratingscore",
                "leadtimescore",
                "supplierscore"
            ]

            st.dataframe(
                supplier_ranking[display_columns],
                use_container_width=True,
                hide_index=True
            )

        # ----------------------------------------------------
        # RECOMMENDED SUPPLIERS
        # ----------------------------------------------------

        st.markdown(
            "### ⭐ Recommended Suppliers"
        )

        if not supplier_recommendations.empty:

            recommended = supplier_recommendations[
                supplier_recommendations[
                    "recommendedsupplier"
                ]
                .astype(str)
                .str.upper()
                .eq("YES")
            ].copy()

            recommended = recommended.merge(
                suppliers[
                    [
                        "supplierid",
                        "suppliercode",
                        "suppliername",
                        "location"
                    ]
                ],
                on="supplierid",
                how="left"
            )

            recommended = recommended.merge(
                materials[
                    [
                        "materialid",
                        "materialcode",
                        "materialname"
                    ]
                ],
                on="materialid",
                how="left"
            )

            display_columns = [
                "recommendationid",
                "materialcode",
                "materialname",
                "suppliercode",
                "suppliername",
                "location",
                "requiredquantity",
                "supplierrating",
                "averageleadtime",
                "supplierscore",
                "selectionreason"
            ]

            display_columns = [
                c for c in display_columns
                if c in recommended.columns
            ]

            st.dataframe(
                recommended[display_columns],
                use_container_width=True,
                hide_index=True
            )


# ============================================================
# PURCHASE ORDERS
# ============================================================

elif page == "Purchase Orders":

    st.markdown(
        '<div class="section-title">'
        '📄 Purchase Orders'
        '</div>',
        unsafe_allow_html=True
    )

    if purchase_orders.empty:

        st.warning(
            "No purchase orders available."
        )

    else:

        po_display = purchase_orders.copy()

        # ----------------------------------------------------
        # MERGE SUPPLIER
        # ----------------------------------------------------

        po_display = po_display.merge(
            suppliers[
                [
                    "supplierid",
                    "suppliercode",
                    "suppliername",
                    "location"
                ]
            ],
            on="supplierid",
            how="left"
        )

        # ----------------------------------------------------
        # MERGE PO ITEMS
        # ----------------------------------------------------

        po_display = po_display.merge(
            po_items[
                [
                    "poid",
                    "materialid",
                    "quantity",
                    "unitprice"
                ]
            ],
            on="poid",
            how="left"
        )

        # ----------------------------------------------------
        # MERGE MATERIAL
        # ----------------------------------------------------

        po_display = po_display.merge(
            materials[
                [
                    "materialid",
                    "materialcode",
                    "materialname"
                ]
            ],
            on="materialid",
            how="left"
        )

        po_display["totalordervalue"] = (
            pd.to_numeric(
                po_display["quantity"],
                errors="coerce"
            ).fillna(0)
            *
            pd.to_numeric(
                po_display["unitprice"],
                errors="coerce"
            ).fillna(0)
        )

        # ----------------------------------------------------
        # KPI
        # ----------------------------------------------------

        col1, col2, col3 = st.columns(3)

        col1.metric(
            "Purchase Orders",
            len(po_display)
        )

        col2.metric(
            "Total PO Value",
            f"₹{po_display['totalordervalue'].sum():,.2f}"
        )

        pending = (
            po_display["status"]
            .astype(str)
            .str.upper()
            .eq("PENDING")
            .sum()
        )

        col3.metric(
            "Pending POs",
            pending
        )

        # ----------------------------------------------------
        # TABLE
        # ----------------------------------------------------

        display_columns = [
            "poid",
            "ponumber",
            "suppliercode",
            "suppliername",
            "materialcode",
            "materialname",
            "quantity",
            "unitprice",
            "totalordervalue",
            "podate",
            "expecteddeliverydate",
            "actualdeliverydate",
            "status"
        ]

        display_columns = [
            c for c in display_columns
            if c in po_display.columns
        ]

        st.dataframe(
            po_display[display_columns],
            use_container_width=True,
            hide_index=True
        )


# ============================================================
# APPROVAL TRACKING
# ============================================================

elif page == "Approval Tracking":

    st.markdown(
        '<div class="section-title">'
        '✅ Purchase Order Approval Tracking'
        '</div>',
        unsafe_allow_html=True
    )

    if po_recommendations.empty:

        st.warning(
            "No purchase order recommendation data available."
        )

    else:

        # ----------------------------------------------------
        # APPROVAL COUNTS
        # ----------------------------------------------------

        approval_status = (
            po_recommendations[
                "approvalstatus"
            ]
            .astype(str)
            .str.upper()
        )

        pending = (
            approval_status.eq("PENDING").sum()
        )

        approved = (
            approval_status.eq("APPROVED").sum()
        )

        rejected = (
            approval_status.eq("REJECTED").sum()
        )

        col1, col2, col3 = st.columns(3)

        col1.metric(
            "Pending Approval",
            pending
        )

        col2.metric(
            "Approved",
            approved
        )

        col3.metric(
            "Rejected",
            rejected
        )

        # ----------------------------------------------------
        # APPROVAL TABLE
        # ----------------------------------------------------

        approval_display = po_recommendations.copy()

        approval_display = approval_display.merge(
            suppliers[
                [
                    "supplierid",
                    "suppliercode",
                    "suppliername"
                ]
            ],
            on="supplierid",
            how="left"
        )

        approval_display = approval_display.merge(
            materials[
                [
                    "materialid",
                    "materialcode",
                    "materialname"
                ]
            ],
            on="materialid",
            how="left"
        )

        display_columns = [
            "porecommendationid",
            "recommendationid",
            "materialcode",
            "materialname",
            "suppliercode",
            "suppliername",
            "requiredquantity",
            "unitcost",
            "estimatedtotalcost",
            "supplierleadtime",
            "requiredbydate",
            "procurementpriority",
            "risklevel",
            "approvalstatus",
            "approvedby",
            "approvaldate",
            "postatus"
        ]

        display_columns = [
            c for c in display_columns
            if c in approval_display.columns
        ]

        st.dataframe(
            approval_display[display_columns],
            use_container_width=True,
            hide_index=True
        )

        # ----------------------------------------------------
        # PRIORITY APPROVAL
        # ----------------------------------------------------

        st.markdown(
            "### 🚨 Approval Priority"
        )

        priority_counts = (
            po_recommendations[
                "procurementpriority"
            ]
            .astype(str)
            .str.upper()
            .value_counts()
            .rename_axis("Priority")
            .reset_index(name="Count")
        )

        st.bar_chart(
            priority_counts.set_index("Priority")
        )


# ============================================================
# DELIVERY TRACKING
# ============================================================

elif page == "Delivery Tracking":

    st.markdown(
        '<div class="section-title">'
        '🚚 Purchase Order Delivery Tracking'
        '</div>',
        unsafe_allow_html=True
    )

    if purchase_orders.empty:

        st.warning(
            "No purchase order data available."
        )

    else:

        delivery = purchase_orders.copy()

        today = pd.Timestamp.today().normalize()

        delivery["deliverystatus"] = "PENDING_DELIVERY"

        # Delivered
        delivered_mask = (
            delivery["actualdeliverydate"].notna()
        )

        delivery.loc[
            delivered_mask,
            "deliverystatus"
        ] = "DELIVERED"

        # Delivered late
        late_mask = (
            delivered_mask
            &
            (
                delivery["actualdeliverydate"]
                >
                delivery["expecteddeliverydate"]
            )
        )

        delivery.loc[
            late_mask,
            "deliverystatus"
        ] = "DELIVERED_LATE"

        # Overdue
        overdue_mask = (
            delivery["actualdeliverydate"].isna()
            &
            delivery["expecteddeliverydate"].notna()
            &
            (
                delivery["expecteddeliverydate"]
                < today
            )
        )

        delivery.loc[
            overdue_mask,
            "deliverystatus"
        ] = "OVERDUE"

        delivery["deliverydelaydays"] = 0

        # Delivered delay
        delivery.loc[
            delivered_mask,
            "deliverydelaydays"
        ] = (
            delivery.loc[
                delivered_mask,
                "actualdeliverydate"
            ]
            -
            delivery.loc[
                delivered_mask,
                "expecteddeliverydate"
            ]
        ).dt.days.clip(lower=0)

        # Overdue delay
        delivery.loc[
            overdue_mask,
            "deliverydelaydays"
        ] = (
            today
            -
            delivery.loc[
                overdue_mask,
                "expecteddeliverydate"
            ]
        ).dt.days

        # ----------------------------------------------------
        # KPIs
        # ----------------------------------------------------

        pending_delivery = (
            delivery["deliverystatus"]
            .eq("PENDING_DELIVERY")
            .sum()
        )

        delivered = (
            delivery["deliverystatus"]
            .eq("DELIVERED")
            .sum()
        )

        delivered_late = (
            delivery["deliverystatus"]
            .eq("DELIVERED_LATE")
            .sum()
        )

        overdue = (
            delivery["deliverystatus"]
            .eq("OVERDUE")
            .sum()
        )

        col1, col2, col3, col4 = st.columns(4)

        col1.metric(
            "Pending Delivery",
            pending_delivery
        )

        col2.metric(
            "Delivered",
            delivered
        )

        col3.metric(
            "Delivered Late",
            delivered_late
        )

        col4.metric(
            "Overdue",
            overdue
        )

        # ----------------------------------------------------
        # MERGE SUPPLIER
        # ----------------------------------------------------

        delivery = delivery.merge(
            suppliers[
                [
                    "supplierid",
                    "suppliercode",
                    "suppliername"
                ]
            ],
            on="supplierid",
            how="left"
        )

        display_columns = [
            "poid",
            "ponumber",
            "suppliercode",
            "suppliername",
            "podate",
            "expecteddeliverydate",
            "actualdeliverydate",
            "deliverystatus",
            "deliverydelaydays",
            "status"
        ]

        st.dataframe(
            delivery[
                [
                    c
                    for c in display_columns
                    if c in delivery.columns
                ]
            ],
            use_container_width=True,
            hide_index=True
        )


# ============================================================
# RISK ANALYSIS
# ============================================================

elif page == "Risk Analysis":

    st.markdown(
        '<div class="section-title">'
        '⚠️ Stockout Risk Analysis'
        '</div>',
        unsafe_allow_html=True
    )

    if stockout_risk.empty:

        st.warning(
            "No stockout risk data available."
        )

    else:

        risk_display = stockout_risk.copy()

        risk_display = risk_display.merge(
            materials[
                [
                    "materialid",
                    "materialcode",
                    "materialname",
                    "category"
                ]
            ],
            on="materialid",
            how="left"
        )

        # ----------------------------------------------------
        # RISK COUNTS
        # ----------------------------------------------------

        risk_counts = (
            risk_display["risklevel"]
            .astype(str)
            .str.upper()
            .value_counts()
        )

        critical = risk_counts.get(
            "CRITICAL",
            0
        )

        high = risk_counts.get(
            "HIGH",
            0
        )

        medium = risk_counts.get(
            "MEDIUM",
            0
        )

        low = risk_counts.get(
            "LOW",
            0
        )

        col1, col2, col3, col4 = st.columns(4)

        col1.metric(
            "Critical",
            critical
        )

        col2.metric(
            "High",
            high
        )

        col3.metric(
            "Medium",
            medium
        )

        col4.metric(
            "Low",
            low
        )

        # ----------------------------------------------------
        # RISK DISTRIBUTION
        # ----------------------------------------------------

        st.markdown(
            "### 📊 Risk Distribution"
        )

        risk_chart = pd.DataFrame(
            {
                "Risk Level": [
                    "CRITICAL",
                    "HIGH",
                    "MEDIUM",
                    "LOW"
                ],
                "Count": [
                    critical,
                    high,
                    medium,
                    low
                ]
            }
        )

        st.bar_chart(
            risk_chart.set_index("Risk Level")
        )

        # ----------------------------------------------------
        # RISK TABLE
        # ----------------------------------------------------

        display_columns = [
            "stockoutriskid",
            "materialcode",
            "materialname",
            "forecastdate",
            "forecastquantity",
            "currentstock",
            "projectedstockafterdemand",
            "minimumstock",
            "risklevel",
            "shortagequantity",
            "shortagevalue"
        ]

        display_columns = [
            c for c in display_columns
            if c in risk_display.columns
        ]

        st.dataframe(
            risk_display[display_columns],
            use_container_width=True,
            hide_index=True
        )

        # ----------------------------------------------------
        # SHORTAGE VALUE
        # ----------------------------------------------------

        shortage_value = pd.to_numeric(
            risk_display["shortagevalue"],
            errors="coerce"
        ).fillna(0).sum()

        shortage_quantity = pd.to_numeric(
            risk_display["shortagequantity"],
            errors="coerce"
        ).fillna(0).sum()

        col1, col2 = st.columns(2)

        col1.metric(
            "Total Shortage Quantity",
            f"{shortage_quantity:,.2f}"
        )

        col2.metric(
            "Total Shortage Value",
            f"₹{shortage_value:,.2f}"
        )


# ============================================================
# FORECAST ANALYSIS
# ============================================================

elif page == "Forecast Analysis":

    st.markdown(
        '<div class="section-title">'
        '📈 Demand Forecast Analysis'
        '</div>',
        unsafe_allow_html=True
    )

    if predictions.empty:

        st.warning(
            "No prediction data available."
        )

    else:

        forecast_display = predictions.copy()

        forecast_display = forecast_display.merge(
            materials[
                [
                    "materialid",
                    "materialcode",
                    "materialname",
                    "category"
                ]
            ],
            on="materialid",
            how="left"
        )

        # ----------------------------------------------------
        # MATERIAL FILTER
        # ----------------------------------------------------

        material_options = {
            "All Materials": None
        }

        for _, row in materials.iterrows():

            material_options[
                f"{row['materialcode']} - {row['materialname']}"
            ] = row["materialid"]

        selected_material_name = st.selectbox(
            "Select Material",
            list(material_options.keys())
        )

        selected_material = material_options[
            selected_material_name
        ]

        filtered = forecast_display.copy()

        if selected_material is not None:

            filtered = filtered[
                filtered["materialid"]
                == selected_material
            ]

        # ----------------------------------------------------
        # FORECAST CHART
        # ----------------------------------------------------

        if not filtered.empty:

            chart_data = filtered[
                [
                    "predictiondate",
                    "forecastquantity"
                ]
            ].copy()

            chart_data = chart_data.sort_values(
                "predictiondate"
            )

            chart_data = chart_data.set_index(
                "predictiondate"
            )

            st.markdown(
                "### 📈 Forecast Quantity"
            )

            st.line_chart(
                chart_data[
                    "forecastquantity"
                ]
            )

        # ----------------------------------------------------
        # FORECAST TABLE
        # ----------------------------------------------------

        display_columns = [
            "predictionid",
            "materialcode",
            "materialname",
            "predictiondate",
            "forecastquantity",
            "stockoutprobability",
            "recommendedpurchase"
        ]

        display_columns = [
            c for c in display_columns
            if c in filtered.columns
        ]

        st.dataframe(
            filtered[display_columns],
            use_container_width=True,
            hide_index=True
        )


# ============================================================
# DATA EXPLORER
# ============================================================

elif page == "Data Explorer":

    st.markdown(
        '<div class="section-title">'
        '🗄️ Data Explorer'
        '</div>',
        unsafe_allow_html=True
    )

    datasets = {
        "Materials": materials,
        "Inventory": inventory,
        "Predictions": predictions,
        "Stockout Risk": stockout_risk,
        "Procurement Recommendations": procurement,
        "Suppliers": suppliers,
        "Supplier Recommendations":
            supplier_recommendations,
        "PO Recommendations":
            po_recommendations,
        "Purchase Orders":
            purchase_orders,
        "Purchase Order Items":
            po_items
    }

    selected_dataset = st.selectbox(
        "Select Dataset",
        list(datasets.keys())
    )

    selected_data = datasets[
        selected_dataset
    ]

    st.write(
        f"Rows: **{len(selected_data)}**"
    )

    st.write(
        f"Columns: **{len(selected_data.columns)}**"
    )

    st.dataframe(
        selected_data,
        use_container_width=True,
        hide_index=True
    )

    # --------------------------------------------------------
    # DOWNLOAD
    # --------------------------------------------------------

    if not selected_data.empty:

        csv_data = selected_data.to_csv(
            index=False
        ).encode("utf-8")

        filename = (
            selected_dataset
            .lower()
            .replace(" ", "_")
            + ".csv"
        )

        st.download_button(
            label="⬇️ Download CSV",
            data=csv_data,
            file_name=filename,
            mime="text/csv"
        )


# ============================================================
# FOOTER
# ============================================================

st.sidebar.markdown("---")

st.sidebar.caption(
    "SmartProcure | Phase 18"
)

st.sidebar.caption(
    "Python + PostgreSQL + Streamlit"
)