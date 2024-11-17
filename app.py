import streamlit as st
import mysql.connector
from datetime import date, datetime, timedelta
import os
import uuid

# -------------------------
# Database Connection Setup
# -------------------------
def create_connection():
    """
    Establishes a connection to the MySQL database.
    
    Returns:
        conn: A MySQL connection object.
    """
    conn = mysql.connector.connect(
        host='localhost',
        user='root',
        password='Exo7Harness$',  # Replace with your actual MySQL password
        database='rems33'  # Update to your database name
    )
    return conn

# -------------------------
# User Authentication
# -------------------------
def authenticate(username, password):
    """
    Authenticates a user by verifying the provided username and password.
    
    Args:
        username (str): The username entered by the user.
        password (str): The password entered by the user.
    
    Returns:
        user (dict or None): A dictionary containing user details if authentication is successful, else None.
    """
    conn = create_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM User WHERE Username=%s AND Password=%s", (username, password))
    user = cursor.fetchone()
    conn.close()
    return user

# -------------------------
# User Signup
# -------------------------
def signup(username, password, user_type, name, contact_no, email):
    """
    Registers a new user by inserting their details into the User and either Tenant or Owner tables.
    
    Args:
        username (str): Desired username.
        password (str): Desired password.
        user_type (str): Type of user ('Tenant' or 'Owner').
        name (str): Full name of the user.
        contact_no (str): Contact number.
        email (str): Email address.
    """
    conn = create_connection()
    cursor = conn.cursor()
    # Insert into User table
    cursor.execute("INSERT INTO User (Username, Password, UserType) VALUES (%s, %s, %s)", (username, password, user_type))
    user_id = cursor.lastrowid
    # Insert into Tenant or Owner table based on user_type
    if user_type == 'Tenant':
        cursor.execute("INSERT INTO Tenant (TenantID, Name, ContactNo, Email) VALUES (%s, %s, %s, %s)", (user_id, name, contact_no, email))
    elif user_type == 'Owner':
        cursor.execute("INSERT INTO Owner (OwnerID, Name, ContactNo, Email) VALUES (%s, %s, %s, %s)", (user_id, name, contact_no, email))
    conn.commit()
    conn.close()

# -------------------------
# Main Application Function
# -------------------------
def main():
    """
    The main function that initializes the Streamlit app, handles user authentication,
    and directs users to their respective dashboards based on their roles.
    """
    st.title("Real Estate Management System")

    # Initialize session state for login status
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
        st.session_state.user = None

    if not st.session_state.logged_in:
        # Sidebar menu for Login and SignUp
        menu = ["Login", "SignUp"]
        choice = st.sidebar.selectbox("Menu", menu)

        if choice == "Login":
            # Login form
            username = st.sidebar.text_input("User Name")
            password = st.sidebar.text_input("Password", type='password')
            login_button = st.sidebar.button("Login")

            if login_button:
                user = authenticate(username, password)
                if user:
                    st.session_state.logged_in = True
                    st.session_state.user = user
                    st.success(f"Logged In as {user['UserType']}")
                    st.rerun()  # Rerun the app to update the UI
                else:
                    st.error("Invalid Username or Password")

        elif choice == "SignUp":
            # SignUp form
            st.subheader("Create New Account")
            with st.form(key='signup_form'):
                username = st.text_input("User Name")
                password = st.text_input("Password", type='password')
                user_type = st.selectbox("User Type", ["Tenant", "Owner"])
                name = st.text_input("Full Name")
                contact_no = st.text_input("Contact Number")
                email = st.text_input("Email")
                signup_button = st.form_submit_button("Sign Up")

                if signup_button:
                    signup(username, password, user_type, name, contact_no, email)
                    st.success("You have successfully created an account")
                    st.info("Go to Login Menu to login")
    else:
        # User is logged in; display appropriate dashboard based on user type
        user = st.session_state.user
        # Add Logout Option in the sidebar
        st.sidebar.write(f"Logged in as {user['Username']} ({user['UserType']})")
        if st.sidebar.button("Logout"):
            st.session_state.logged_in = False
            st.session_state.user = None
            st.rerun()  # Rerun to update the UI

        # Direct user to their respective dashboard
        if user['UserType'] == 'Tenant':
            tenant_dashboard(user)
        elif user['UserType'] == 'Owner':
            owner_dashboard(user)
        elif user['UserType'] == 'Admin':
            admin_dashboard(user)

# -------------------------
# Tenant Dashboard
# -------------------------
def tenant_dashboard(user):
    """
    Displays the dashboard for Tenant users with options to view properties,
    view their rental requests, and view their rented properties.
    
    Args:
        user (dict): Dictionary containing user details.
    """
    tenant_menu = ["View Properties", "Requested to Rent", "Show My Property"]
    choice = st.sidebar.selectbox("Tenant Menu", tenant_menu)

    if choice == "View Properties":
        view_properties(user)
    elif choice == "Requested to Rent":
        requested_to_rent(user)
    elif choice == "Show My Property":
        show_my_property(user)  # Ensure this is called only once

# -------------------------
# Owner Dashboard
# -------------------------
def owner_dashboard(user):
    """
    Displays the dashboard for Owner users with options to list properties,
    show their properties, and view rental requests.
    
    Args:
        user (dict): Dictionary containing user details.
    """
    owner_menu = ["List Properties", "Show Properties", "Requests"]
    choice = st.sidebar.selectbox("Owner Menu", owner_menu)

    if choice == "List Properties":
        list_properties(user)
    elif choice == "Show Properties":
        show_properties(user)
    elif choice == "Requests":
        view_requests(user)

# -------------------------
# Admin Dashboard
# -------------------------
def admin_dashboard(user):
    """
    Displays the dashboard for Admin users with options to view overall dashboard,
    manage leases, and handle billing and payments.
    
    Args:
        user (dict): Dictionary containing user details.
    """
    admin_menu = ["Dashboard", "Lease Management", "Billing and Payments"]
    choice = st.sidebar.selectbox("Admin Menu", admin_menu)

    if choice == "Dashboard":
        admin_dashboard_page()
    elif choice == "Lease Management":
        admin_lease_management()
    elif choice == "Billing and Payments":
        admin_billing_payments()

# -------------------------
# Admin Dashboard Page
# -------------------------
def admin_dashboard_page():
    """
    Displays various metrics and statistics on the Admin dashboard,
    such as total tenants, properties, maintenance requests, unpaid bills,
    and lease statuses.
    """
    st.subheader("Admin Dashboard")
    conn = create_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Fetch total number of tenants
    cursor.execute("SELECT COUNT(*) AS total_tenants FROM Tenant")
    total_tenants = cursor.fetchone()['total_tenants']
    
    # Fetch total number of properties
    cursor.execute("SELECT COUNT(*) AS total_properties FROM Property")
    total_properties = cursor.fetchone()['total_properties']
    
    # Fetch total number of maintenance requests
    cursor.execute("SELECT COUNT(*) AS total_maint_requests FROM Maintenance")
    total_maint_requests = cursor.fetchone()['total_maint_requests']
    
    # Fetch total number of unpaid bills
    cursor.execute("SELECT COUNT(*) AS unpaid_bills FROM Bill WHERE Status='Unpaid'")
    unpaid_bills = cursor.fetchone()['unpaid_bills']
    
    # Fetch lease statuses and their counts
    cursor.execute("""
        SELECT Status, COUNT(*) AS count FROM Lease GROUP BY Status
    """)
    lease_statuses = cursor.fetchall()

    # Display the fetched metrics
    st.write(f"*Total Tenants:* {total_tenants}")
    st.write(f"*Total Properties:* {total_properties}")
    st.write(f"*Total Maintenance Requests:* {total_maint_requests}")
    st.write(f"*Unpaid Bills:* {unpaid_bills}")
    st.write("*Lease Statuses:*")
    for status in lease_statuses:
        st.write(f"- {status['Status']}: {status['count']}")
    
    conn.close()

# -------------------------
# Admin Lease Management
# -------------------------
def admin_lease_management():
    """
    Allows Admin users to view, approve, or reject lease requests from tenants.
    """
    st.subheader("Admin Lease Management")
    conn = create_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Fetch all leases with related tenant and property information
    cursor.execute("""
        SELECT Lease.LeaseID, Lease.PropertyID, Lease.TenantID, Lease.Status, 
        Tenant.Name AS TenantName, Property.Name AS PropertyName
        FROM Lease
        JOIN Tenant ON Lease.TenantID = Tenant.TenantID
        JOIN Property ON Lease.PropertyID = Property.PropertyID
    """)
    leases = cursor.fetchall()
    
    for lease in leases:
        with st.expander(f"Lease ID: {lease['LeaseID']} - {lease['PropertyName']} - Tenant: {lease['TenantName']}"):
            # Display lease details
            st.write(f"*Property ID*: {lease['PropertyID']}")
            st.write(f"*Tenant ID*: {lease['TenantID']}")
            st.write(f"*Tenant Name*: {lease['TenantName']}")
            st.write(f"*Status*: {lease['Status']}")
            
            # If lease is pending, provide options to approve or reject
            if lease['Status'] == 'Pending':
                approve = st.button(f"Approve", key=f"admin_approve_{lease['LeaseID']}")
                reject = st.button(f"Reject", key=f"admin_reject_{lease['LeaseID']}")
                
                if approve:
                    conn_update = create_connection()
                    cursor_update = conn_update.cursor()
                    # Update lease status to 'Accepted'
                    cursor_update.execute("UPDATE Lease SET Status='Accepted' WHERE LeaseID=%s", (lease['LeaseID'],))
                    # Call stored procedure to generate lease agreement
                    cursor_update.callproc('generate_lease_agreement', [lease['LeaseID']])
                    conn_update.commit()
                    conn_update.close()
                    st.success("Lease Approved and Lease Agreement Generated")
                    st.rerun()
                
                if reject:
                    conn_update = create_connection()
                    cursor_update = conn_update.cursor()
                    # Update lease status to 'Rejected'
                    cursor_update.execute("UPDATE Lease SET Status='Rejected' WHERE LeaseID=%s", (lease['LeaseID'],))
                    conn_update.commit()
                    conn_update.close()
                    st.info("Lease Rejected")
                    st.rerun()
            else:
                st.write("No actions available.")
    conn.close()

# -------------------------
# Admin Billing and Payments
# -------------------------
def admin_billing_payments():
    """
    Allows Admin users to view all bills, calculate penalties for late payments,
    and mark bills as paid. It also records payments including any penalties.
    """
    st.subheader("Admin Billing and Payments")

    conn = create_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Fetch all bills with related tenant information
    cursor.execute("""
        SELECT Bill.BillID, Bill.LeaseID, Bill.BillType, Bill.Amount, Bill.DueDate, Bill.Status,
        Tenant.Name AS TenantName
        FROM Bill
        JOIN Lease ON Bill.LeaseID = Lease.LeaseID
        JOIN Tenant ON Lease.TenantID = Tenant.TenantID
    """)
    bills = cursor.fetchall()
    
    for bill in bills:
        with st.expander(f"Bill ID: {bill['BillID']} - {bill['BillType']} - Tenant: {bill['TenantName']}"):
            # Display bill details
            st.write(f"*Lease ID*: {bill['LeaseID']}")
            st.write(f"*Amount*: ${bill['Amount']}")
            st.write(f"*Due Date*: {bill['DueDate'].strftime('%Y-%m-%d %H:%M:%S')}")
            st.write(f"*Status*: {bill['Status']}")

            # Calculate late payment penalty using stored function
            conn_calc = create_connection()
            cursor_calc = conn_calc.cursor()
            cursor_calc.execute("SELECT calculate_late_payment_penalty(%s)", (bill['BillID'],))
            result = cursor_calc.fetchone()
            conn_calc.close()

            try:
                penalty = float(result[0]) if result and result[0] is not None else 0.0
            except (TypeError, ValueError):
                penalty = 0.0

            try:
                amount = float(bill['Amount']) if bill['Amount'] is not None else 0.0
            except (TypeError, ValueError):
                amount = 0.0

            # Calculate total due including penalty
            total_due = amount + penalty

            st.write(f"*Late Payment Penalty*: ${penalty}")
            st.write(f"*Total Due (including penalty)*: ${total_due}")

            # If bill is unpaid, provide option to mark as paid
            if bill['Status'] == 'Unpaid':
                mark_paid = st.button(f"Mark as Paid", key=f"mark_paid_{bill['BillID']}")
                if mark_paid:
                    conn_pay = create_connection()
                    cursor_pay = conn_pay.cursor()
                    # Update bill status to 'Paid'
                    cursor_pay.execute("UPDATE Bill SET Status='Paid' WHERE BillID=%s", (bill['BillID'],))
                    # Record the payment including penalty
                    total_amount = amount + penalty
                    cursor_pay.execute("""
                        INSERT INTO Payment (TenantID, BillID, PaymentDate, Amount) 
                        VALUES (
                            (SELECT TenantID FROM Lease WHERE LeaseID=%s), 
                            %s, %s, %s)
                    """, (bill['LeaseID'], bill['BillID'], datetime.now(), total_amount))
                    conn_pay.commit()
                    conn_pay.close()
                    st.success("Bill marked as Paid")
                    st.rerun()
    conn.close()

    # The following block seems to be duplicated. If intentional, it can be kept; otherwise, consider removing.
    # Fetch and display bills again
    st.subheader("Admin Billing and Payments")

    conn = create_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT Bill.BillID, Bill.LeaseID, Bill.BillType, Bill.Amount, Bill.DueDate, Bill.Status,
        Tenant.Name AS TenantName
        FROM Bill
        JOIN Lease ON Bill.LeaseID = Lease.LeaseID
        JOIN Tenant ON Lease.TenantID = Tenant.TenantID
    """)
    bills = cursor.fetchall()
    for bill in bills:
        with st.expander(f"Bill ID: {bill['BillID']} - {bill['BillType']} - Tenant: {bill['TenantName']}"):
            st.write(f"*Lease ID*: {bill['LeaseID']}")
            st.write(f"*Amount*: ${bill['Amount']}")
            st.write(f"*Due Date*: {bill['DueDate'].strftime('%Y-%m-%d %H:%M:%S')}")
            st.write(f"*Status*: {bill['Status']}")

            # Fetch penalty with null check
            conn_calc = create_connection()
            cursor_calc = conn_calc.cursor()
            cursor_calc.execute("SELECT calculate_late_payment_penalty(%s)", (bill['BillID'],))
            result = cursor_calc.fetchone()
            conn_calc.close()

            # Ensure penalty is a float, set to 0.0 if None or conversion fails
            try:
                penalty = float(result[0]) if result and result[0] is not None else 0.0
            except (TypeError, ValueError):
                penalty = 0.0

            # Ensure bill['Amount'] is a float, set to 0.0 if None or conversion fails
            try:
                amount = float(bill['Amount']) if bill['Amount'] is not None else 0.0
            except (TypeError, ValueError):
                amount = 0.0

            # Correct calculation
            total_due = amount + penalty

            st.write(f"*Late Payment Penalty*: ${penalty}")
            st.write(f"*Total Due (including penalty)*: ${total_due}")

            if bill['Status'] == 'Unpaid':
                mark_paid = st.button(f"Mark as Paid", key=f"mark_paid_{bill['BillID']}")
                if mark_paid:
                    conn_pay = create_connection()
                    cursor_pay = conn_pay.cursor()
                    # Update bill status to 'Paid'
                    cursor_pay.execute("UPDATE Bill SET Status='Paid' WHERE BillID=%s", (bill['BillID'],))
                    # Record the payment including penalty
                    total_amount = amount + penalty
                    cursor_pay.execute("""
                        INSERT INTO Payment (TenantID, BillID, PaymentDate, Amount) 
                        VALUES (
                            (SELECT TenantID FROM Lease WHERE LeaseID=%s), 
                            %s, %s, %s)
                    """, (bill['LeaseID'], bill['BillID'], datetime.now(), total_amount))
                    conn_pay.commit()
                    conn_pay.close()
                    st.success("Bill marked as Paid")
                    st.rerun()
    conn.close()

# -------------------------
# Tenant Functions
# -------------------------
def view_properties(user):
    """
    Allows Tenant users to view available properties that are not already rented or requested by them.
    Tenants can request to rent a property from this view.
    
    Args:
        user (dict): Dictionary containing user details.
    """
    st.subheader("Available Properties")
    conn = create_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Fetch properties not already leased or requested by the tenant
    cursor.execute("""
        SELECT * FROM Property WHERE PropertyID NOT IN (
            SELECT PropertyID FROM Lease WHERE (Status='Accepted' OR TenantID=%s)
        )
    """, (user['UserID'],))
    properties = cursor.fetchall()
    
    for prop in properties:
        property_id = prop['PropertyID']
        # Initialize image index in session state for this property
        image_index_key = f"image_index_{property_id}"
        if image_index_key not in st.session_state:
            st.session_state[image_index_key] = 0

        # Fetch all images associated with the property
        cursor.execute("SELECT ImagePath FROM PropertyImages WHERE PropertyID=%s", (property_id,))
        images = cursor.fetchall()
        image_paths = [img['ImagePath'] for img in images]

        # Create a container for each property
        with st.container():
            st.markdown(f"### {prop['Name']}")
            cols = st.columns([1, 2])  # Adjust column widths as needed
            with cols[0]:
                if image_paths:
                    # Display current image based on session state
                    current_index = st.session_state[image_index_key] % len(image_paths)
                    st.image(image_paths[current_index], width=200, use_column_width=False, clamp=True)
                    # Add navigation arrows for image gallery
                    arrow_cols = st.columns([1, 1, 1])
                    with arrow_cols[0]:
                        if st.button("◀️", key=f"prev_{property_id}"):
                            st.session_state[image_index_key] -= 1
                            st.rerun()
                    with arrow_cols[1]:
                        st.write(f"Image {current_index + 1} of {len(image_paths)}")
                    with arrow_cols[2]:
                        if st.button("▶️", key=f"next_{property_id}"):
                            st.session_state[image_index_key] += 1
                            st.rerun()
                else:
                    # Display default image if no images are available
                    st.image('default_property_image.jpg', width=200)
            with cols[1]:
                # Display property details
                st.write(f"*Type*: {prop['Type']}")
                st.write(f"*Location*: {prop['Location']}")
                st.write(f"*Size*: {prop['Size']}")
                # Arrange details in two rows of three columns each
                top_row = st.columns(3)
                top_row[0].write(f"*Price*: ${prop.get('Price', 'N/A')}")
                top_row[1].write(f"*Bedrooms*: {prop.get('Bedrooms', 'N/A')}")
                top_row[2].write(f"*Bathrooms*: {prop.get('Bathrooms', 'N/A')}")
                
                bottom_row = st.columns(3)
                bottom_row[0].write(f"*Availability*: {prop.get('Availability', 'N/A')}")
                bottom_row[1].write(f"*Furnished*: {prop.get('Furnished', 'N/A')}")
                bottom_row[2].write(f"*Pet Friendly*: {prop.get('PetFriendly', 'N/A')}")

                # Button to request renting the property
                request = st.button(f"Request to Rent Property ID {prop['PropertyID']}", key=f"request_{prop['PropertyID']}")
                if request:
                    conn_request = create_connection()
                    cursor_request = conn_request.cursor()
                    # Insert a new lease request with status 'Pending'
                    cursor_request.execute(
                        "INSERT INTO Lease (TenantID, PropertyID, StartDate, EndDate, Status) VALUES (%s, %s, %s, %s, %s)",
                        (user['UserID'], prop['PropertyID'], date.today(), date.today() + timedelta(days=365), 'Pending')
                    )
                    conn_request.commit()
                    conn_request.close()
                    st.success("Lease Request Sent")
                    st.rerun()  # Rerun to update the UI
            st.markdown("---")  # Separator line between properties
    conn.close()

def requested_to_rent(user):
    """
    Allows Tenant users to view their lease requests along with their statuses.
    If a lease is accepted, the lease agreement is displayed.
    
    Args:
        user (dict): Dictionary containing user details.
    """
    st.subheader("Your Lease Requests")
    conn = create_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Fetch all lease requests made by the tenant
    cursor.execute("""
        SELECT Lease.LeaseID, Lease.PropertyID, Lease.Status, Property.Name AS PropertyName
        FROM Lease
        JOIN Property ON Lease.PropertyID = Property.PropertyID
        WHERE Lease.TenantID=%s
    """, (user['UserID'],))
    leases = cursor.fetchall()
    
    if leases:
        for lease in leases:
            with st.expander(f"Lease ID: {lease['LeaseID']} - {lease['PropertyName']}"):
                st.write(f"*Property ID*: {lease['PropertyID']}")
                st.write(f"*Status*: {lease['Status']}")
                
                if lease['Status'] == 'Accepted':
                    # Fetch and display the lease agreement if lease is accepted
                    cursor.execute("SELECT AgreementText FROM lease_agreements WHERE LeaseID=%s", (lease['LeaseID'],))
                    agreement = cursor.fetchone()
                    if agreement:
                        st.subheader("Lease Agreement")
                        st.write(agreement['AgreementText'])
                    else:
                        st.info("No lease agreement found.")
                else:
                    st.info("Your lease request is still pending or has been rejected.")
    else:
        st.info("You have no lease requests.")
    conn.close()

def show_my_property(user):
    """
    Allows Tenant users to view properties they have successfully rented.
    Displays lease agreements, bills, and maintenance requests related to their rentals.
    
    Args:
        user (dict): Dictionary containing user details.
    """
    st.subheader("My Property")
    conn = create_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Fetch all accepted leases for the tenant
    cursor.execute("""
        SELECT Lease.LeaseID, Lease.PropertyID, Property.Name AS PropertyName
        FROM Lease
        JOIN Property ON Lease.PropertyID = Property.PropertyID
        WHERE Lease.TenantID=%s AND Lease.Status='Accepted'
    """, (user['UserID'],))
    leases = cursor.fetchall()

    # To prevent duplicate listings, ensure that each property is displayed only once
    seen_properties = set()

    for lease in leases:
        property_id = lease['PropertyID']
        lease_id = lease['LeaseID']

        if property_id in seen_properties:
            continue  # Skip if property already displayed
        seen_properties.add(property_id)

        # Initialize image index in session state for this property and lease
        image_index_key = f"image_index_{property_id}_{lease_id}"
        if image_index_key not in st.session_state:
            st.session_state[image_index_key] = 0

        # Fetch all images associated with the property
        cursor.execute("SELECT ImagePath FROM PropertyImages WHERE PropertyID=%s", (property_id,))
        images = cursor.fetchall()
        image_paths = [img['ImagePath'] for img in images]

        # Fetch property details
        cursor.execute("SELECT * FROM Property WHERE PropertyID=%s", (property_id,))
        prop = cursor.fetchone()

        # Create a container for the property
        with st.container():
            st.markdown(f"### {prop['Name']}")
            cols = st.columns([1, 2])  # Adjust column widths as needed
            with cols[0]:
                if image_paths:
                    # Display current image based on session state
                    current_index = st.session_state[image_index_key] % len(image_paths)
                    st.image(image_paths[current_index], width=200, use_column_width=False, clamp=True)
                    # Add navigation arrows for image gallery
                    arrow_cols = st.columns([1, 1, 1])
                    with arrow_cols[0]:
                        if st.button("◀️", key=f"prev_{property_id}_{lease_id}"):
                            st.session_state[image_index_key] -= 1
                            st.rerun()
                    with arrow_cols[1]:
                        st.write(f"Image {current_index + 1} of {len(image_paths)}")
                    with arrow_cols[2]:
                        if st.button("▶️", key=f"next_{property_id}_{lease_id}"):
                            st.session_state[image_index_key] += 1
                            st.rerun()
                else:
                    # Display default image if no images are available
                    st.image('default_property_image.jpg', width=200)
            with cols[1]:
                # Display property details
                st.write(f"*Type*: {prop['Type']}")
                st.write(f"*Location*: {prop['Location']}")
                st.write(f"*Size*: {prop['Size']}")
                # Arrange details in two rows of three columns each
                top_row = st.columns(3)
                top_row[0].write(f"*Price*: ${prop.get('Price', 'N/A')}")
                top_row[1].write(f"*Bedrooms*: {prop.get('Bedrooms', 'N/A')}")
                top_row[2].write(f"*Bathrooms*: {prop.get('Bathrooms', 'N/A')}")
                
                bottom_row = st.columns(3)
                bottom_row[0].write(f"*Availability*: {prop.get('Availability', 'N/A')}")
                bottom_row[1].write(f"*Furnished*: {prop.get('Furnished', 'N/A')}")
                bottom_row[2].write(f"*Pet Friendly*: {prop.get('PetFriendly', 'N/A')}")

        # Fetch and display the lease agreement
        cursor.execute("SELECT AgreementText FROM lease_agreements WHERE LeaseID=%s", (lease_id,))
        agreement = cursor.fetchone()
        if agreement:
            st.subheader("Lease Agreement")
            st.write(agreement['AgreementText'])  # Display lease agreement without nested expander
        else:
            st.info("No lease agreement found.")

        st.markdown("---")  # Separator line

        # Display Bills related to the lease
        st.subheader("Bills")
        cursor.execute("SELECT * FROM Bill WHERE LeaseID=%s", (lease_id,))
        bills = cursor.fetchall()
        if bills:
            for bill in bills:
                with st.expander(f"Bill ID: {bill['BillID']} - {bill['BillType']}"):
                    st.write(f"*Amount*: ${bill['Amount']}")
                    st.write(f"*Due Date*: {bill['DueDate'].strftime('%Y-%m-%d %H:%M:%S')}")
                    st.write(f"*Status*: {bill['Status']}")
                    if bill['Status'] == 'Unpaid':
                        with st.form(key=f'payment_form_{bill["BillID"]}'):
                            # Form to input payment amount and submit payment
                            payment_amount = st.number_input("Payment Amount", value=float(bill['Amount']), format="%.2f")
                            pay = st.form_submit_button("Pay Now")
                            if pay:
                                conn_pay = create_connection()
                                cursor_pay = conn_pay.cursor()
                                try:
                                    # Insert payment record and update bill status to 'Paid'
                                    cursor_pay.execute(
                                        "INSERT INTO Payment (TenantID, BillID, PaymentDate, Amount) VALUES (%s, %s, %s, %s)",
                                        (user['UserID'], bill['BillID'], datetime.now(), payment_amount)
                                    )
                                    cursor_pay.execute("UPDATE Bill SET Status='Paid' WHERE BillID=%s", (bill['BillID'],))
                                    conn_pay.commit()
                                    st.success("Bill Paid")
                                    st.rerun()  # Rerun to update the UI
                                except mysql.connector.Error as err:
                                    st.error(f"Error: {err.msg}")
                                    conn_pay.rollback()
                                conn_pay.close()
        else:
            st.write("No bills found.")

        # Display Maintenance Requests and their statuses
        st.subheader("Maintenance Requests")
        cursor.execute("""
            SELECT ReqID, ReqDate, Description, Status, AlertStatus
            FROM Maintenance
            WHERE LeaseID=%s
        """, (lease_id,))
        maintenances = cursor.fetchall()
        if maintenances:
            for maintenance in maintenances:
                if maintenance.get('AlertStatus') == 'Alert':
                    # Highlight maintenance requests pending for more than 2 minutes
                    st.warning(f"Maintenance ID: {maintenance['ReqID']} - ALERT: Pending for more than 2 minutes")
                with st.expander(f"Request ID: {maintenance['ReqID']} - {maintenance['Status']}"):
                    st.write(f"*Date*: {maintenance['ReqDate'].strftime('%Y-%m-%d %H:%M:%S')}")
                    st.write(f"*Description*: {maintenance['Description']}")
        else:
            st.write("No maintenance requests found.")

        # Form to submit a new maintenance request
        st.subheader("Request Maintenance")
        with st.form(key='maintenance_form'):
            description = st.text_area("Describe the issue")
            submit_request = st.form_submit_button("Submit Maintenance Request")
            if submit_request:
                conn_maint = create_connection()
                cursor_maint = conn_maint.cursor()
                # Insert new maintenance request with status 'Requested'
                cursor_maint.execute(
                    "INSERT INTO Maintenance (LeaseID, ReqDate, Description, Status) VALUES (%s, %s, %s, %s)",
                    (lease_id, datetime.now(), description, 'Requested')
                )
                conn_maint.commit()
                conn_maint.close()
                st.success("Maintenance Request Submitted")
                st.rerun()  # Rerun to update the UI
    else:
        st.info("No Accepted Leases Found")
    conn.close()

# -------------------------
# Owner Functions
# -------------------------
def list_properties(user):
    """
    Allows Owner users to view, add, edit, or delete their listed properties.
    Owners can also see tenant ratings for their properties.
    
    Args:
        user (dict): Dictionary containing user details.
    """
    st.subheader("Your Listed Properties")
    conn = create_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Fetch all properties listed by the owner
    cursor.execute("SELECT * FROM Property WHERE OwnerID=%s", (user['UserID'],))
    properties = cursor.fetchall()
    
    for prop in properties:
        property_id = prop['PropertyID']
        # Initialize image index in session state for this property
        image_index_key = f"image_index_{property_id}"
        if image_index_key not in st.session_state:
            st.session_state[image_index_key] = 0

        # Fetch all images associated with the property
        cursor.execute("SELECT ImagePath FROM PropertyImages WHERE PropertyID=%s", (property_id,))
        images = cursor.fetchall()
        image_paths = [img['ImagePath'] for img in images]

        # Check if property is currently rented
        cursor.execute("SELECT COUNT(*) AS LeaseCount FROM Lease WHERE PropertyID=%s AND Status='Accepted'", (property_id,))
        lease_info = cursor.fetchone()
        if lease_info['LeaseCount'] > 0:
            can_edit_delete = False  # Property is rented; cannot edit or delete
        else:
            can_edit_delete = True  # Property is not rented; can edit or delete

        with st.container():
            st.markdown(f"### {prop['Name']}")
            cols = st.columns([1, 2])
            with cols[0]:
                if image_paths:
                    # Display current image based on session state
                    current_index = st.session_state[image_index_key] % len(image_paths)
                    st.image(image_paths[current_index], width=200, use_column_width=False, clamp=True)
                    # Add navigation arrows for image gallery
                    arrow_cols = st.columns([1, 1, 1])
                    with arrow_cols[0]:
                        if st.button("◀️", key=f"prev_{property_id}"):
                            st.session_state[image_index_key] -= 1
                            st.rerun()
                    with arrow_cols[1]:
                        st.write(f"Image {current_index + 1} of {len(image_paths)}")
                    with arrow_cols[2]:
                        if st.button("▶️", key=f"next_{property_id}"):
                            st.session_state[image_index_key] += 1
                            st.rerun()
                else:
                    # Display default image if no images are available
                    st.image('default_property_image.jpg', width=200)
            with cols[1]:
                # Display property details
                st.write(f"*Type*: {prop['Type']}")
                st.write(f"*Location*: {prop['Location']}")
                st.write(f"*Size*: {prop['Size']}")
                # Arrange details in two rows of three columns each
                top_row = st.columns(3)
                top_row[0].write(f"*Price*: ${prop.get('Price', 'N/A')}")
                top_row[1].write(f"*Bedrooms*: {prop.get('Bedrooms', 'N/A')}")
                top_row[2].write(f"*Bathrooms*: {prop.get('Bathrooms', 'N/A')}")
                
                bottom_row = st.columns(3)
                bottom_row[0].write(f"*Availability*: {prop.get('Availability', 'N/A')}")
                bottom_row[1].write(f"*Furnished*: {prop.get('Furnished', 'N/A')}")
                bottom_row[2].write(f"*Pet Friendly*: {prop.get('PetFriendly', 'N/A')}")
                
                # Fetch tenant rating using stored function
                conn_rating = create_connection()
                cursor_rating = conn_rating.cursor()
                cursor_rating.execute("""
                    SELECT calculate_tenant_rating(TenantID)
                    FROM Lease
                    WHERE PropertyID=%s AND Status='Accepted'
                """, (prop['PropertyID'],))
                rating_result = cursor_rating.fetchone()
                if rating_result and rating_result[0] is not None:
                    tenant_rating = rating_result[0]
                    st.write(f"*Tenant Rating:* {tenant_rating} / 5.0")
                else:
                    st.write("*Tenant Rating:* N/A")
                conn_rating.close()

                if can_edit_delete:
                    # Display Edit and Delete buttons if property is not rented
                    edit_col, delete_col = st.columns(2)
                    with edit_col:
                        if st.button(f"Edit Property ID {prop['PropertyID']}", key=f"edit_{prop['PropertyID']}"):
                            st.session_state[f'edit_property_{prop["PropertyID"]}'] = True
                    with delete_col:
                        if st.button(f"Delete Property ID {prop['PropertyID']}", key=f"delete_{prop['PropertyID']}"):
                            # Confirm deletion
                            st.warning(f"Are you sure you want to delete Property ID {prop['PropertyID']}?")
                            if st.button(f"Yes, Delete Property ID {prop['PropertyID']}", key=f"confirm_delete_{prop['PropertyID']}"):
                                conn_delete = create_connection()
                                cursor_delete = conn_delete.cursor()
                                # Delete property and associated images from the database
                                cursor_delete.execute("DELETE FROM Property WHERE PropertyID=%s", (prop['PropertyID'],))
                                cursor_delete.execute("DELETE FROM PropertyImages WHERE PropertyID=%s", (prop['PropertyID'],))
                                conn_delete.commit()
                                conn_delete.close()
                                st.success("Property Deleted")
                                st.rerun()  # Rerun to update the UI
                else:
                    st.info("This property is currently rented and cannot be edited or deleted.")

            st.markdown("---")  # Separator line between properties

            # Display Edit Property Form if edit is triggered
            if st.session_state.get(f'edit_property_{prop["PropertyID"]}', False):
                st.subheader(f"Edit Property ID {prop['PropertyID']}")
                with st.form(key=f'edit_property_form_{prop["PropertyID"]}'):
                    # Pre-fill form with existing property details
                    name = st.text_input("Property Name", value=prop['Name'])
                    prop_type = st.text_input("Property Type", value=prop['Type'])
                    location = st.text_input("Location", value=prop['Location'])
                    size = st.text_input("Size", value=prop['Size'])
                    
                    # Handle None values for numerical fields
                    price_value = prop.get('Price') if prop.get('Price') is not None else 0.0
                    bedrooms_value = prop.get('Bedrooms') if prop.get('Bedrooms') is not None else 0
                    bathrooms_value = prop.get('Bathrooms') if prop.get('Bathrooms') is not None else 0
                    
                    # Input fields for numerical and select options
                    price = st.number_input("Price", min_value=0.0, format="%.2f", value=float(price_value))
                    bedrooms = st.number_input("Bedrooms", min_value=0, step=1, value=int(bedrooms_value))
                    bathrooms = st.number_input("Bathrooms", min_value=0, step=1, value=int(bathrooms_value))
                    availability = st.text_input("Availability", value=prop.get('Availability', ''))
                    furnished = st.selectbox("Furnished", ['Yes', 'No'], index=['Yes', 'No'].index(prop.get('Furnished', 'No')))
                    pet_friendly = st.selectbox("Pet Friendly", ['Yes', 'No'], index=['Yes', 'No'].index(prop.get('PetFriendly', 'No')))
                    
                    # Option to upload new images
                    image_files = st.file_uploader("Upload New Property Images (Optional)", type=['png', 'jpg', 'jpeg'], accept_multiple_files=True)
                    submit_edit = st.form_submit_button("Update Property")
                    
                    if submit_edit:
                        conn_edit = create_connection()
                        cursor_edit = conn_edit.cursor()
                        # Update property details in the database
                        cursor_edit.execute(
                            """UPDATE Property SET Name=%s, Type=%s, Location=%s, Size=%s, Price=%s, Bedrooms=%s, Bathrooms=%s,
                            Availability=%s, Furnished=%s, PetFriendly=%s WHERE PropertyID=%s""",
                            (name, prop_type, location, size, price, bedrooms, bathrooms, availability, furnished, pet_friendly, prop['PropertyID'])
                        )
                        # Handle new image uploads if any
                        if image_files:
                            # Delete existing images from the database
                            cursor_edit.execute("DELETE FROM PropertyImages WHERE PropertyID=%s", (prop['PropertyID'],))
                            # Ensure the images directory exists
                            if not os.path.exists("images"):
                                os.makedirs("images")
                            for image_file in image_files:
                                # Generate a unique filename to prevent conflicts
                                unique_filename = str(uuid.uuid4()) + os.path.splitext(image_file.name)[1]
                                image_path = os.path.join("images", unique_filename)
                                with open(image_path, "wb") as f:
                                    f.write(image_file.getbuffer())
                                # Insert new image path into the PropertyImages table
                                cursor_edit.execute(
                                    "INSERT INTO PropertyImages (PropertyID, ImagePath) VALUES (%s, %s)",
                                    (prop['PropertyID'], image_path)
                                )
                        conn_edit.commit()
                        conn_edit.close()
                        st.success("Property Updated")
                        st.session_state[f'edit_property_{prop["PropertyID"]}'] = False  # Hide the form after updating
                        st.rerun()  # Rerun to update the UI
    conn.close()

    # "+" Button to Add New Property
    if 'show_add_property_form' not in st.session_state:
        st.session_state.show_add_property_form = False

    if st.button("+ Add New Property"):
        st.session_state.show_add_property_form = True

    if st.session_state.show_add_property_form:
        st.subheader("Add New Property")
        with st.form(key='list_property_form'):
            # Input fields for new property details
            name = st.text_input("Property Name")
            prop_type = st.text_input("Property Type")
            location = st.text_input("Location")
            size = st.text_input("Size")
            price = st.number_input("Price", min_value=0.0, format="%.2f")
            bedrooms = st.number_input("Bedrooms", min_value=0, step=1)
            bathrooms = st.number_input("Bathrooms", min_value=0, step=1)
            availability = st.text_input("Availability")
            furnished = st.selectbox("Furnished", ['Yes', 'No'])
            pet_friendly = st.selectbox("Pet Friendly", ['Yes', 'No'])
            # Multiple image upload
            image_files = st.file_uploader("Upload Property Images", type=['png', 'jpg', 'jpeg'], accept_multiple_files=True)
            submit_property = st.form_submit_button("Add Property")
            
            if submit_property:
                if not image_files:
                    st.error("Unable to submit form since image has not been uploaded")
                else:
                    conn = create_connection()
                    cursor = conn.cursor()
                    # Insert new property details into the database
                    cursor.execute(
                        "INSERT INTO Property (OwnerID, Name, Type, Location, Size, Price, Bedrooms, Bathrooms, Availability, Furnished, PetFriendly) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                        (user['UserID'], name, prop_type, location, size, price, bedrooms, bathrooms, availability, furnished, pet_friendly)
                    )
                    property_id = cursor.lastrowid
                    # Handle image uploads
                    if not os.path.exists("images"):
                        os.makedirs("images")
                    for image_file in image_files:
                        # Generate a unique filename for each image
                        unique_filename = str(uuid.uuid4()) + os.path.splitext(image_file.name)[1]
                        image_path = os.path.join("images", unique_filename)
                        with open(image_path, "wb") as f:
                            f.write(image_file.getbuffer())
                        # Insert image path into the PropertyImages table
                        cursor.execute(
                            "INSERT INTO PropertyImages (PropertyID, ImagePath) VALUES (%s, %s)",
                            (property_id, image_path)
                        )
                    conn.commit()
                    conn.close()
                    st.success("Property Added")
                    st.session_state.show_add_property_form = False  # Hide the form after adding
                    st.rerun()  # Rerun to update the UI

def show_properties(user):
    """
    Allows Owner users to view properties that are currently being rented.
    Displays lease agreements, bills, and maintenance requests related to each property.
    
    Args:
        user (dict): Dictionary containing user details.
    """
    st.subheader("Your Properties Being Rented")
    conn = create_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Fetch all accepted leases for properties owned by the user
    cursor.execute("""
        SELECT Lease.LeaseID, Lease.PropertyID, Lease.TenantID, Lease.StartDate, Lease.EndDate, Tenant.Name AS TenantName, Property.Name AS PropertyName
        FROM Lease
        JOIN Property ON Lease.PropertyID = Property.PropertyID
        JOIN Tenant ON Lease.TenantID = Tenant.TenantID
        WHERE Property.OwnerID=%s AND Lease.Status='Accepted'
    """, (user['UserID'],))
    leases = cursor.fetchall()
    
    for lease in leases:
        property_id = lease['PropertyID']
        # Initialize image index in session state for this property
        image_index_key = f"image_index_{property_id}"
        if image_index_key not in st.session_state:
            st.session_state[image_index_key] = 0

        # Fetch all images associated with the property
        cursor.execute("SELECT ImagePath FROM PropertyImages WHERE PropertyID=%s", (property_id,))
        images = cursor.fetchall()
        image_paths = [img['ImagePath'] for img in images]

        with st.container():
            st.markdown(f"### {lease['PropertyName']}")
            cols = st.columns([1, 2])
            with cols[0]:
                if image_paths:
                    # Display current image based on session state
                    current_index = st.session_state[image_index_key] % len(image_paths)
                    st.image(image_paths[current_index], width=200, use_column_width=False, clamp=True)
                    # Add navigation arrows for image gallery
                    arrow_cols = st.columns([1, 1, 1])
                    with arrow_cols[0]:
                        if st.button("◀️", key=f"prev_{property_id}"):
                            st.session_state[image_index_key] -= 1
                            st.rerun()
                    with arrow_cols[1]:
                        st.write(f"Image {current_index + 1} of {len(image_paths)}")
                    with arrow_cols[2]:
                        if st.button("▶️", key=f"next_{property_id}"):
                            st.session_state[image_index_key] += 1
                            st.rerun()
                else:
                    # Display default image if no images are available
                    st.image('default_property_image.jpg', width=200)
            with cols[1]:
                # Display tenant and property details
                st.write(f"*Tenant*: {lease['TenantName']}")
                # Fetch property details
                cursor.execute("SELECT * FROM Property WHERE PropertyID=%s", (property_id,))
                prop = cursor.fetchone()
                st.write(f"*Type*: {prop['Type']}")
                st.write(f"*Location*: {prop['Location']}")
                st.write(f"*Size*: {prop['Size']}")
                
                # Arrange details in two rows of three columns each
                top_row = st.columns(3)
                top_row[0].write(f"*Price*: ${prop.get('Price', 'N/A')}")
                top_row[1].write(f"*Bedrooms*: {prop.get('Bedrooms', 'N/A')}")
                top_row[2].write(f"*Bathrooms*: {prop.get('Bathrooms', 'N/A')}")
                
                bottom_row = st.columns(3)
                bottom_row[0].write(f"*Availability*: {prop.get('Availability', 'N/A')}")
                bottom_row[1].write(f"*Furnished*: {prop.get('Furnished', 'N/A')}")
                bottom_row[2].write(f"*Pet Friendly*: {prop.get('PetFriendly', 'N/A')}")

        # Fetch and display the lease agreement
        cursor.execute("SELECT AgreementText FROM lease_agreements WHERE LeaseID=%s", (lease['LeaseID'],))
        agreement = cursor.fetchone()
        if agreement:
            st.subheader("Lease Agreement")
            with st.expander("View Lease Agreement"):
                st.write(agreement['AgreementText'])
        else:
            st.info("No lease agreement found.")

        st.markdown("---")  # Separator line

        # Display Bills related to the lease
        st.subheader("Bills")
        cursor.execute("SELECT * FROM Bill WHERE LeaseID=%s", (lease['LeaseID'],))
        bills = cursor.fetchall()
        if bills:
            for bill in bills:
                with st.expander(f"Bill ID: {bill['BillID']} - {bill['BillType']}"):
                    st.write(f"*Amount*: ${bill['Amount']}")
                    st.write(f"*Due Date*: {bill['DueDate'].strftime('%Y-%m-%d %H:%M:%S')}")
                    st.write(f"*Status*: {bill['Status']}")
        else:
            st.write("No bills found.")

        # Display Maintenance Requests related to the lease
        st.subheader("Maintenance Requests")
        cursor.execute("SELECT * FROM Maintenance WHERE LeaseID=%s", (lease['LeaseID'],))
        maintenances = cursor.fetchall()
        if maintenances:
            for maintenance in maintenances:
                if maintenance.get('AlertStatus') == 'Alert':
                    # Highlight maintenance requests pending for more than 2 minutes
                    st.warning(f"Maintenance ID: {maintenance['ReqID']} - ALERT: Pending for more than 2 minutes")
                with st.expander(f"Maintenance ID: {maintenance['ReqID']} - {maintenance['Status']}"):
                    st.write(f"*Description*: {maintenance['Description']}")
                    st.write(f"*Request Date*: {maintenance['ReqDate'].strftime('%Y-%m-%d %H:%M:%S')}")
                    # Form to update maintenance status
                    if maintenance['Status'] != 'Completed':
                        with st.form(key=f'maintenance_form_{maintenance["ReqID"]}'):
                            new_status = st.selectbox("Update Status", ['Requested', 'In Progress', 'Completed'], index=['Requested', 'In Progress', 'Completed'].index(maintenance['Status']))
                            update_status = st.form_submit_button("Update Maintenance Status")
                            if update_status:
                                conn_maint = create_connection()
                                cursor_maint = conn_maint.cursor()
                                # Update maintenance status and reset AlertStatus
                                cursor_maint.execute(
                                    "UPDATE Maintenance SET Status=%s, AlertStatus=NULL WHERE ReqID=%s",
                                    (new_status, maintenance['ReqID'])
                                )
                                conn_maint.commit()
                                conn_maint.close()
                                st.success("Maintenance Status Updated")
                                st.rerun()  # Rerun to update the UI
        else:
            st.write("No maintenance requests found.")

    conn.close()

def view_requests(user):
    """
    Allows Owner users to view lease requests from tenants.
    Owners can approve or reject these requests.
    
    Args:
        user (dict): Dictionary containing user details.
    """
    st.subheader("Lease Requests from Tenants")
    conn = create_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Fetch all pending lease requests for the owner's properties
    cursor.execute("""
        SELECT Lease.LeaseID, Lease.PropertyID, Lease.TenantID, Tenant.Name AS TenantName, Property.Name AS PropertyName
        FROM Lease
        JOIN Property ON Lease.PropertyID = Property.PropertyID
        JOIN Tenant ON Lease.TenantID = Tenant.TenantID
        WHERE Property.OwnerID=%s AND Lease.Status='Pending'
    """, (user['UserID'],))
    requests = cursor.fetchall()
    
    if requests:
        for request in requests:
            with st.expander(f"Lease ID: {request['LeaseID']} - {request['PropertyName']} - Tenant: {request['TenantName']}"):
                st.write(f"*Property ID*: {request['PropertyID']}")
                st.write(f"*Tenant ID*: {request['TenantID']}")
                st.write(f"*Tenant Name*: {request['TenantName']}")
                # Arrange Approve and Reject buttons side by side
                button_col1, button_col2 = st.columns(2)
                with button_col1:
                    approve = st.button(f"Approve", key=f"approve_{request['LeaseID']}")
                with button_col2:
                    reject = st.button(f"Reject", key=f"reject_{request['LeaseID']}")
                
                if approve:
                    conn_update = create_connection()
                    cursor_update = conn_update.cursor()
                    # Update lease status to 'Accepted'
                    cursor_update.execute("UPDATE Lease SET Status='Accepted' WHERE LeaseID=%s", (request['LeaseID'],))
                    # Call stored procedure to generate lease agreement
                    cursor_update.callproc('generate_lease_agreement', [request['LeaseID']])
                    conn_update.commit()
                    conn_update.close()
                    st.success("Lease Approved and Lease Agreement Generated")
                    st.rerun()  # Rerun to update the UI
                
                if reject:
                    conn_update = create_connection()
                    cursor_update = conn_update.cursor()
                    # Update lease status to 'Rejected'
                    cursor_update.execute("UPDATE Lease SET Status='Rejected' WHERE LeaseID=%s", (request['LeaseID'],))
                    conn_update.commit()
                    conn_update.close()
                    st.info("Lease Rejected")
                    st.rerun()  # Rerun to update the UI
    else:
        st.info("No lease requests at the moment.")
    conn.close()

# -------------------------
# Entry Point
# -------------------------
if __name__ == '__main__':
    main()