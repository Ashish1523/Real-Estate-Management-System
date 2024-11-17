import streamlit as st
import mysql.connector
from datetime import date
import os
import uuid

# Database Connection
def create_connection():
    conn = mysql.connector.connect(
        host='localhost',
        user='root',
        password='Exo7Harness$',  # Replace with your actual MySQL password
        database='rems_3'  # Update to your database name
    )
    return conn

# User Authentication
def authenticate(username, password):
    conn = create_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM User WHERE Username=%s AND Password=%s", (username, password))
    user = cursor.fetchone()
    conn.close()
    return user

# User Signup
def signup(username, password, user_type, name, contact_no, email):
    conn = create_connection()
    cursor = conn.cursor()
    # Insert into User table
    cursor.execute("INSERT INTO User (Username, Password, UserType) VALUES (%s, %s, %s)", (username, password, user_type))
    user_id = cursor.lastrowid
    # Insert into Tenant or Owner table
    if user_type == 'Tenant':
        cursor.execute("INSERT INTO Tenant (TenantID, Name, ContactNo, Email) VALUES (%s, %s, %s, %s)", (user_id, name, contact_no, email))
    elif user_type == 'Owner':
        cursor.execute("INSERT INTO Owner (OwnerID, Name, ContactNo, Email) VALUES (%s, %s, %s, %s)", (user_id, name, contact_no, email))
    conn.commit()
    conn.close()

# Main Function
def main():
    st.title("Real Estate Management System")

    # Initialize session state for login status
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
        st.session_state.user = None

    if not st.session_state.logged_in:
        # Login/Signup Selection
        menu = ["Login", "SignUp"]
        choice = st.sidebar.selectbox("Menu", menu)

        if choice == "Login":
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
        user = st.session_state.user
        # Add Logout Option
        st.sidebar.write(f"Logged in as {user['Username']} ({user['UserType']})")
        if st.sidebar.button("Logout"):
            st.session_state.logged_in = False
            st.session_state.user = None
            st.rerun()  # Rerun to update the UI

        if user['UserType'] == 'Tenant':
            tenant_dashboard(user)
        elif user['UserType'] == 'Owner':
            owner_dashboard(user)
        elif user['UserType'] == 'Admin':
            admin_dashboard(user)

# Tenant Dashboard
def tenant_dashboard(user):
    tenant_menu = ["View Properties", "Requested to Rent", "Show My Property"]
    choice = st.sidebar.selectbox("Tenant Menu", tenant_menu)

    if choice == "View Properties":
        view_properties(user)
    elif choice == "Requested to Rent":
        requested_to_rent(user)
    elif choice == "Show My Property":
        show_my_property(user)

# Owner Dashboard
def owner_dashboard(user):
    owner_menu = ["List Properties", "Show Properties", "Requests"]
    choice = st.sidebar.selectbox("Owner Menu", owner_menu)

    if choice == "List Properties":
        list_properties(user)
    elif choice == "Show Properties":
        show_properties(user)
    elif choice == "Requests":
        view_requests(user)

# Admin Dashboard
def admin_dashboard(user):
    admin_menu = ["Dashboard", "Lease Management", "Billing and Payments"]
    choice = st.sidebar.selectbox("Admin Menu", admin_menu)

    if choice == "Dashboard":
        admin_dashboard_page()
    elif choice == "Lease Management":
        admin_lease_management()
    elif choice == "Billing and Payments":
        admin_billing_payments()

# Implement the Admin Pages
def admin_dashboard_page():
    st.subheader("Admin Dashboard")
    conn = create_connection()
    cursor = conn.cursor(dictionary=True)
    # Total Tenants
    cursor.execute("SELECT COUNT(*) AS total_tenants FROM Tenant")
    total_tenants = cursor.fetchone()['total_tenants']
    # Total Properties
    cursor.execute("SELECT COUNT(*) AS total_properties FROM Property")
    total_properties = cursor.fetchone()['total_properties']
    # Total Maintenance Requests
    cursor.execute("SELECT COUNT(*) AS total_maint_requests FROM Maintenance")
    total_maint_requests = cursor.fetchone()['total_maint_requests']
    # Unpaid Bills
    cursor.execute("SELECT COUNT(*) AS unpaid_bills FROM Bill WHERE Status='Unpaid'")
    unpaid_bills = cursor.fetchone()['unpaid_bills']
    # Lease Statuses
    cursor.execute("""
        SELECT Status, COUNT(*) AS count FROM Lease GROUP BY Status
    """)
    lease_statuses = cursor.fetchall()

    # Display Metrics
    st.write(f"*Total Tenants:* {total_tenants}")
    st.write(f"*Total Properties:* {total_properties}")
    st.write(f"*Total Maintenance Requests:* {total_maint_requests}")
    st.write(f"*Unpaid Bills:* {unpaid_bills}")
    st.write("*Lease Statuses:*")
    for status in lease_statuses:
        st.write(f"- {status['Status']}: {status['count']}")

    conn.close()

def admin_lease_management():
    st.subheader("Admin Lease Management")
    conn = create_connection()
    cursor = conn.cursor(dictionary=True)
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
            st.write(f"*Property ID*: {lease['PropertyID']}")
            st.write(f"*Tenant ID*: {lease['TenantID']}")
            st.write(f"*Tenant Name*: {lease['TenantName']}")
            st.write(f"*Status*: {lease['Status']}")
            # Actions
            if lease['Status'] == 'Pending':
                approve = st.button(f"Approve", key=f"admin_approve_{lease['LeaseID']}")
                reject = st.button(f"Reject", key=f"admin_reject_{lease['LeaseID']}")
                if approve:
                    conn_update = create_connection()
                    cursor_update = conn_update.cursor()
                    cursor_update.execute("UPDATE Lease SET Status='Accepted' WHERE LeaseID=%s", (lease['LeaseID'],))
                    conn_update.commit()
                    conn_update.close()
                    st.success("Lease Approved")
                    st.rerun()
                if reject:
                    conn_update = create_connection()
                    cursor_update = conn_update.cursor()
                    cursor_update.execute("UPDATE Lease SET Status='Rejected' WHERE LeaseID=%s", (lease['LeaseID'],))
                    conn_update.commit()
                    conn_update.close()
                    st.info("Lease Rejected")
                    st.rerun()
            else:
                st.write("No actions available.")
    conn.close()

def admin_billing_payments():
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
            st.write(f"*Due Date*: {bill['DueDate']}")
            st.write(f"*Status*: {bill['Status']}")
            if bill['Status'] == 'Unpaid':
                mark_paid = st.button(f"Mark as Paid", key=f"mark_paid_{bill['BillID']}")
                if mark_paid:
                    conn_pay = create_connection()
                    cursor_pay = conn_pay.cursor()
                    cursor_pay.execute("UPDATE Bill SET Status='Paid' WHERE BillID=%s", (bill['BillID'],))
                    # Record payment
                    cursor_pay.execute("""
                        INSERT INTO Payment (TenantID, BillID, PaymentDate, Amount) 
                        VALUES (
                            (SELECT TenantID FROM Lease WHERE LeaseID=%s), 
                            %s, %s, %s)
                    """, (bill['LeaseID'], bill['BillID'], date.today(), bill['Amount']))
                    conn_pay.commit()
                    conn_pay.close()
                    st.success("Bill marked as Paid")
                    st.rerun()
    conn.close()

# Tenant Functions
def view_properties(user):
    st.subheader("Available Properties")
    conn = create_connection()
    cursor = conn.cursor(dictionary=True)
    # Exclude properties already requested or rented by this tenant or already leased to others
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

        # Create a card-like layout using columns
        with st.container():
            st.markdown(f"### {prop['Name']}")
            cols = st.columns([1, 2])  # Adjust column widths as needed
            with cols[0]:
                if image_paths:
                    # Display current image
                    current_index = st.session_state[image_index_key] % len(image_paths)
                    st.image(image_paths[current_index], width=200, use_column_width=False, clamp=True)
                    # Add navigation arrows
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
                    st.image('default_property_image.jpg', width=200)
            with cols[1]:
                st.write(f"*Type*: {prop['Type']}")
                st.write(f"*Location*: {prop['Location']}")
                st.write(f"*Size*: {prop['Size']}")
                # Arrange details in rows
                # Top row details
                top_row = st.columns(3)
                top_row[0].write(f"*Price*: ${prop.get('Price', 'N/A')}")
                top_row[1].write(f"*Bedrooms*: {prop.get('Bedrooms', 'N/A')}")
                top_row[2].write(f"*Bathrooms*: {prop.get('Bathrooms', 'N/A')}")
                # Bottom row details
                bottom_row = st.columns(3)
                bottom_row[0].write(f"*Availability*: {prop.get('Availability', 'N/A')}")
                bottom_row[1].write(f"*Furnished*: {prop.get('Furnished', 'N/A')}")
                bottom_row[2].write(f"*Pet Friendly*: {prop.get('PetFriendly', 'N/A')}")
                request = st.button(f"Request to Rent Property ID {prop['PropertyID']}", key=f"request_{prop['PropertyID']}")
                if request:
                    conn_request = create_connection()
                    cursor_request = conn_request.cursor()
                    cursor_request.execute(
                        "INSERT INTO Lease (TenantID, PropertyID, StartDate, EndDate, Status) VALUES (%s, %s, %s, %s, %s)",
                        (user['UserID'], prop['PropertyID'], date.today(), date.today(), 'Pending')
                    )
                    conn_request.commit()
                    conn_request.close()
                    st.success("Lease Request Sent")
                    st.rerun()  # Rerun to update the UI
            st.markdown("---")  # Separator line
    conn.close()

def requested_to_rent(user):
    st.subheader("Your Lease Requests")
    conn = create_connection()
    cursor = conn.cursor(dictionary=True)
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
    else:
        st.info("You have no lease requests.")
    conn.close()

def show_my_property(user):
    st.subheader("My Property")
    conn = create_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT Lease.LeaseID, Lease.PropertyID, Property.Name AS PropertyName
        FROM Lease
        JOIN Property ON Lease.PropertyID = Property.PropertyID
        WHERE Lease.TenantID=%s AND Lease.Status='Accepted'
    """, (user['UserID'],))
    lease = cursor.fetchone()
    if lease:
        property_id = lease['PropertyID']
        # Initialize image index in session state for this property
        image_index_key = f"image_index_{property_id}"
        if image_index_key not in st.session_state:
            st.session_state[image_index_key] = 0

        # Fetch all images associated with the property
        cursor.execute("SELECT ImagePath FROM PropertyImages WHERE PropertyID=%s", (property_id,))
        images = cursor.fetchall()
        image_paths = [img['ImagePath'] for img in images]

        # Fetch property details
        cursor.execute("SELECT * FROM Property WHERE PropertyID=%s", (property_id,))
        prop = cursor.fetchone()

        # Create a card-like layout using columns
        with st.container():
            st.markdown(f"### {prop['Name']}")
            cols = st.columns([1, 2])  # Adjust column widths as needed
            with cols[0]:
                if image_paths:
                    # Display current image
                    current_index = st.session_state[image_index_key] % len(image_paths)
                    st.image(image_paths[current_index], width=200, use_column_width=False, clamp=True)
                    # Add navigation arrows
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
                    st.image('default_property_image.jpg', width=200)
            with cols[1]:
                st.write(f"*Type*: {prop['Type']}")
                st.write(f"*Location*: {prop['Location']}")
                st.write(f"*Size*: {prop['Size']}")
                # Arrange details in rows
                # Top row details
                top_row = st.columns(3)
                top_row[0].write(f"*Price*: ${prop.get('Price', 'N/A')}")
                top_row[1].write(f"*Bedrooms*: {prop.get('Bedrooms', 'N/A')}")
                top_row[2].write(f"*Bathrooms*: {prop.get('Bathrooms', 'N/A')}")
                # Bottom row details
                bottom_row = st.columns(3)
                bottom_row[0].write(f"*Availability*: {prop.get('Availability', 'N/A')}")
                bottom_row[1].write(f"*Furnished*: {prop.get('Furnished', 'N/A')}")
                bottom_row[2].write(f"*Pet Friendly*: {prop.get('PetFriendly', 'N/A')}")

        st.markdown("---")  # Separator line

        # Show Bills
        st.subheader("Bills")
        cursor.execute("SELECT * FROM Bill WHERE LeaseID=%s", (lease['LeaseID'],))
        bills = cursor.fetchall()
        if bills:
            for bill in bills:
                with st.expander(f"Bill ID: {bill['BillID']} - {bill['BillType']}"):
                    st.write(f"*Amount*: ${bill['Amount']}")
                    st.write(f"*Due Date*: {bill['DueDate']}")
                    st.write(f"*Status*: {bill['Status']}")
                    if bill['Status'] == 'Unpaid':
                        pay = st.button(f"Pay Now", key=f"pay_{bill['BillID']}")
                        if pay:
                            conn_pay = create_connection()
                            cursor_pay = conn_pay.cursor()
                            cursor_pay.execute(
                                "INSERT INTO Payment (TenantID, BillID, PaymentDate, Amount) VALUES (%s, %s, %s, %s)",
                                (user['UserID'], bill['BillID'], date.today(), bill['Amount'])
                            )
                            cursor_pay.execute("UPDATE Bill SET Status='Paid' WHERE BillID=%s", (bill['BillID'],))
                            conn_pay.commit()
                            conn_pay.close()
                            st.success("Bill Paid")
                            st.rerun()  # Rerun to update the UI
        else:
            st.write("No bills found.")

        # Display Maintenance Requests and their statuses
        st.subheader("Maintenance Requests")
        cursor.execute("""
            SELECT ReqID, ReqDate, Description, Status
            FROM Maintenance
            WHERE LeaseID=%s
        """, (lease['LeaseID'],))
        maintenances = cursor.fetchall()
        if maintenances:
            for maintenance in maintenances:
                with st.expander(f"Request ID: {maintenance['ReqID']} - {maintenance['Status']}"):
                    st.write(f"*Date*: {maintenance['ReqDate']}")
                    st.write(f"*Description*: {maintenance['Description']}")
        else:
            st.write("No maintenance requests found.")

        # Request Maintenance
        st.subheader("Request Maintenance")
        with st.form(key='maintenance_form'):
            description = st.text_area("Describe the issue")
            submit_request = st.form_submit_button("Submit Maintenance Request")
            if submit_request:
                conn_maint = create_connection()
                cursor_maint = conn_maint.cursor()
                cursor_maint.execute(
                    "INSERT INTO Maintenance (LeaseID, ReqDate, Description, Status) VALUES (%s, %s, %s, %s)",
                    (lease['LeaseID'], date.today(), description, 'Requested')
                )
                conn_maint.commit()
                conn_maint.close()
                st.success("Maintenance Request Submitted")
                st.rerun()  # Rerun to update the UI
    else:
        st.info("No Accepted Leases Found")
    conn.close()

# Owner Functions
def list_properties(user):
    st.subheader("Your Listed Properties")
    conn = create_connection()
    cursor = conn.cursor(dictionary=True)
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

        # Check if property is rented
        cursor.execute("SELECT COUNT(*) AS LeaseCount FROM Lease WHERE PropertyID=%s AND Status='Accepted'", (property_id,))
        lease_info = cursor.fetchone()
        if lease_info['LeaseCount'] > 0:
            can_edit_delete = False
        else:
            can_edit_delete = True

        with st.container():
            st.markdown(f"### {prop['Name']}")
            cols = st.columns([1, 2])
            with cols[0]:
                if image_paths:
                    current_index = st.session_state[image_index_key] % len(image_paths)
                    st.image(image_paths[current_index], width=200, use_column_width=False, clamp=True)
                    # Add navigation arrows
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
                    st.image('default_property_image.jpg', width=200)
            with cols[1]:
                st.write(f"*Type*: {prop['Type']}")
                st.write(f"*Location*: {prop['Location']}")
                st.write(f"*Size*: {prop['Size']}")
                # Arrange details in rows
                # Top row details
                top_row = st.columns(3)
                top_row[0].write(f"*Price*: ${prop.get('Price', 'N/A')}")
                top_row[1].write(f"*Bedrooms*: {prop.get('Bedrooms', 'N/A')}")
                top_row[2].write(f"*Bathrooms*: {prop.get('Bathrooms', 'N/A')}")
                # Bottom row details
                bottom_row = st.columns(3)
                bottom_row[0].write(f"*Availability*: {prop.get('Availability', 'N/A')}")
                bottom_row[1].write(f"*Furnished*: {prop.get('Furnished', 'N/A')}")
                bottom_row[2].write(f"*Pet Friendly*: {prop.get('PetFriendly', 'N/A')}")

                if can_edit_delete:
                    # Edit and Delete buttons
                    edit_col, delete_col = st.columns(2)
                    with edit_col:
                        if st.button(f"Edit Property ID {prop['PropertyID']}", key=f"edit_{prop['PropertyID']}"):
                            st.session_state[f'edit_property_{prop["PropertyID"]}'] = True
                    with delete_col:
                        if st.button(f"Delete Property ID {prop['PropertyID']}", key=f"delete_{prop['PropertyID']}"):
                            # Confirm deletion
                            st.warning(f"Are you sure you want to delete Property ID {prop['PropertyID']}?")
                            if st.button(f"Yes, Delete Property ID {prop['PropertyID']}", key=f"confirm_delete_{prop['PropertyID']}"):
                                # Delete property and associated images
                                conn_delete = create_connection()
                                cursor_delete = conn_delete.cursor()
                                cursor_delete.execute("DELETE FROM Property WHERE PropertyID=%s", (prop['PropertyID'],))
                                cursor_delete.execute("DELETE FROM PropertyImages WHERE PropertyID=%s", (prop['PropertyID'],))
                                conn_delete.commit()
                                conn_delete.close()
                                st.success("Property Deleted")
                                st.rerun()  # Rerun to update the UI
                else:
                    st.info("This property is currently rented and cannot be edited or deleted.")

            st.markdown("---")
            # Edit Property Form
            if st.session_state.get(f'edit_property_{prop["PropertyID"]}', False):
                st.subheader(f"Edit Property ID {prop['PropertyID']}")
                with st.form(key=f'edit_property_form_{prop["PropertyID"]}'):
                    name = st.text_input("Property Name", value=prop['Name'])
                    prop_type = st.text_input("Property Type", value=prop['Type'])
                    location = st.text_input("Location", value=prop['Location'])
                    size = st.text_input("Size", value=prop['Size'])
                    # Handle None values
                    price_value = prop.get('Price') if prop.get('Price') is not None else 0.0
                    bedrooms_value = prop.get('Bedrooms') if prop.get('Bedrooms') is not None else 0
                    bathrooms_value = prop.get('Bathrooms') if prop.get('Bathrooms') is not None else 0
                    # Existing fields
                    price = st.number_input("Price", min_value=0.0, format="%.2f", value=float(price_value))
                    bedrooms = st.number_input("Bedrooms", min_value=0, step=1, value=int(bedrooms_value))
                    bathrooms = st.number_input("Bathrooms", min_value=0, step=1, value=int(bathrooms_value))
                    availability = st.text_input("Availability", value=prop.get('Availability', ''))
                    furnished = st.selectbox("Furnished", ['Yes', 'No'], index=['Yes', 'No'].index(prop.get('Furnished', 'No')))
                    pet_friendly = st.selectbox("Pet Friendly", ['Yes', 'No'], index=['Yes', 'No'].index(prop.get('PetFriendly', 'No')))
                    # Multiple image upload
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
                        # Handle new image uploads
                        if image_files:
                            # Delete existing images
                            cursor_edit.execute("DELETE FROM PropertyImages WHERE PropertyID=%s", (prop['PropertyID'],))
                            # Upload new images
                            if not os.path.exists("images"):
                                os.makedirs("images")
                            for image_file in image_files:
                                unique_filename = str(uuid.uuid4()) + os.path.splitext(image_file.name)[1]
                                image_path = os.path.join("images", unique_filename)
                                with open(image_path, "wb") as f:
                                    f.write(image_file.getbuffer())
                                cursor_edit.execute(
                                    "INSERT INTO PropertyImages (PropertyID, ImagePath) VALUES (%s, %s)",
                                    (prop['PropertyID'], image_path)
                                )
                        conn_edit.commit()
                        conn_edit.close()
                        st.success("Property Updated")
                        st.session_state[f'edit_property_{prop["PropertyID"]}'] = False
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
            name = st.text_input("Property Name")
            prop_type = st.text_input("Property Type")
            location = st.text_input("Location")
            size = st.text_input("Size")
            # New fields
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
                    # Insert property details into the database
                    cursor.execute(
                        "INSERT INTO Property (OwnerID, Name, Type, Location, Size, Price, Bedrooms, Bathrooms, Availability, Furnished, PetFriendly) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                        (user['UserID'], name, prop_type, location, size, price, bedrooms, bathrooms, availability, furnished, pet_friendly)
                    )
                    property_id = cursor.lastrowid
                    # Handle image uploads
                    # Create a directory to store uploaded images if it doesn't exist
                    if not os.path.exists("images"):
                        os.makedirs("images")
                    for image_file in image_files:
                        # Generate a unique filename
                        unique_filename = str(uuid.uuid4()) + os.path.splitext(image_file.name)[1]
                        image_path = os.path.join("images", unique_filename)
                        with open(image_path, "wb") as f:
                            f.write(image_file.getbuffer())
                        # Insert image path into PropertyImages table
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
    st.subheader("Your Properties Being Rented")
    conn = create_connection()
    cursor = conn.cursor(dictionary=True)
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
                    current_index = st.session_state[image_index_key] % len(image_paths)
                    st.image(image_paths[current_index], width=200, use_column_width=False, clamp=True)
                    # Add navigation arrows
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
                    st.image('default_property_image.jpg', width=200)
            with cols[1]:
                st.write(f"*Tenant*: {lease['TenantName']}")
                # Fetch property details
                cursor.execute("SELECT * FROM Property WHERE PropertyID=%s", (lease['PropertyID'],))
                prop = cursor.fetchone()
                st.write(f"*Type*: {prop['Type']}")
                st.write(f"*Location*: {prop['Location']}")
                st.write(f"*Size*: {prop['Size']}")
                # Arrange details in rows
                top_row = st.columns(3)
                top_row[0].write(f"*Price*: ${prop.get('Price', 'N/A')}")
                top_row[1].write(f"*Bedrooms*: {prop.get('Bedrooms', 'N/A')}")
                top_row[2].write(f"*Bathrooms*: {prop.get('Bathrooms', 'N/A')}")
                bottom_row = st.columns(3)
                bottom_row[0].write(f"*Availability*: {prop.get('Availability', 'N/A')}")
                bottom_row[1].write(f"*Furnished*: {prop.get('Furnished', 'N/A')}")
                bottom_row[2].write(f"*Pet Friendly*: {prop.get('PetFriendly', 'N/A')}")
        st.markdown("---")
        # Show Bill Status
        st.subheader("Bills")
        cursor.execute("SELECT * FROM Bill WHERE LeaseID=%s", (lease['LeaseID'],))
        bills = cursor.fetchall()
        if bills:
            for bill in bills:
                with st.expander(f"Bill ID: {bill['BillID']} - {bill['BillType']}"):
                    st.write(f"*Amount*: ${bill['Amount']}")
                    st.write(f"*Due Date*: {bill['DueDate']}")
                    st.write(f"*Status*: {bill['Status']}")
        else:
            st.write("No bills found.")

        # Show Maintenance Requests
        st.subheader("Maintenance Requests")
        cursor.execute("SELECT * FROM Maintenance WHERE LeaseID=%s", (lease['LeaseID'],))
        maintenances = cursor.fetchall()
        if maintenances:
            for maintenance in maintenances:
                with st.expander(f"Maintenance ID: {maintenance['ReqID']} - {maintenance['Status']}"):
                    st.write(f"*Description*: {maintenance['Description']}")
                    st.write(f"*Request Date*: {maintenance['ReqDate']}")
                    # Update Maintenance Status
                    if maintenance['Status'] != 'Completed':
                        with st.form(key=f'maintenance_form_{maintenance["ReqID"]}'):
                            new_status = st.selectbox("Update Status", ['Requested', 'In Progress', 'Completed'], index=['Requested', 'In Progress', 'Completed'].index(maintenance['Status']))
                            update_status = st.form_submit_button("Update Maintenance Status")
                            if update_status:
                                conn_maint = create_connection()
                                cursor_maint = conn_maint.cursor()
                                cursor_maint.execute(
                                    "UPDATE Maintenance SET Status=%s WHERE ReqID=%s",
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
    st.subheader("Lease Requests from Tenants")
    conn = create_connection()
    cursor = conn.cursor(dictionary=True)
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
                    cursor_update.execute("UPDATE Lease SET Status='Accepted' WHERE LeaseID=%s", (request['LeaseID'],))
                    conn_update.commit()
                    conn_update.close()
                    st.success("Lease Approved")
                    st.rerun()  # Rerun to update the UI
                if reject:
                    conn_update = create_connection()
                    cursor_update = conn_update.cursor()
                    cursor_update.execute("UPDATE Lease SET Status='Rejected' WHERE LeaseID=%s", (request['LeaseID'],))
                    conn_update.commit()
                    conn_update.close()
                    st.info("Lease Rejected")
                    st.rerun()  # Rerun to update the UI
    else:
        st.info("No lease requests at the moment.")
    conn.close()

if __name__ == '__main__':
    main()