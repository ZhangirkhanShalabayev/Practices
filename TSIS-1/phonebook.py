import psycopg2
import csv
import json
import os
from datetime import datetime
from connect import get_connection, close_connection
from config import PAGE_SIZE

class PhoneBook:
    def __init__(self):
        self.conn = get_connection()
        if not self.conn:
            raise Exception("Failed to connect to database")
        self.current_page = 0

    def close(self):
        close_connection(self.conn)

    # ===== CRUD Operations =====
    
    def add_contact(self, name, email=None, birthday=None, group_name=None):
        """Add a new contact with optional email, birthday, and group."""
        try:
            cur = self.conn.cursor()
            
            # Get group_id if provided
            group_id = None
            if group_name:
                cur.execute("SELECT id FROM groups WHERE name = %s", (group_name,))
                result = cur.fetchone()
                if result:
                    group_id = result[0]
                else:
                    # Create group if doesn't exist
                    cur.execute("INSERT INTO groups (name) VALUES (%s) RETURNING id", (group_name,))
                    group_id = cur.fetchone()[0]
            
            # Insert contact
            cur.execute("""
                INSERT INTO contacts (name, email, birthday, group_id)
                VALUES (%s, %s, %s, %s)
                RETURNING id
            """, (name, email, birthday, group_id))
            
            contact_id = cur.fetchone()[0]
            self.conn.commit()
            cur.close()
            print(f"✓ Contact '{name}' added (ID: {contact_id})")
            return contact_id
        except psycopg2.Error as e:
            self.conn.rollback()
            print(f"✗ Error adding contact: {e}")
            return None

    def add_phone(self, contact_name, phone, phone_type):
        """Add a phone number to an existing contact."""
        try:
            cur = self.conn.cursor()
            cur.execute("CALL add_phone(%s, %s, %s)", (contact_name, phone, phone_type))
            self.conn.commit()
            cur.close()
            print(f"✓ Phone {phone} ({phone_type}) added to {contact_name}")
        except psycopg2.Error as e:
            self.conn.rollback()
            print(f"✗ Error adding phone: {e}")

    def update_contact(self, contact_id, name=None, email=None, birthday=None):
        """Update contact information."""
        try:
            cur = self.conn.cursor()
            updates = []
            params = []
            
            if name:
                updates.append("name = %s")
                params.append(name)
            if email:
                updates.append("email = %s")
                params.append(email)
            if birthday:
                updates.append("birthday = %s")
                params.append(birthday)
            
            if not updates:
                print("✗ No fields to update")
                return
            
            updates.append("updated_at = CURRENT_TIMESTAMP")
            params.append(contact_id)
            
            query = f"UPDATE contacts SET {', '.join(updates)} WHERE id = %s"
            cur.execute(query, params)
            self.conn.commit()
            
            if cur.rowcount > 0:
                print(f"✓ Contact updated")
            else:
                print(f"✗ Contact not found")
            cur.close()
        except psycopg2.Error as e:
            self.conn.rollback()
            print(f"✗ Error updating contact: {e}")

    def delete_contact(self, contact_id):
        """Delete a contact and all associated phones."""
        try:
            cur = self.conn.cursor()
            cur.execute("DELETE FROM contacts WHERE id = %s", (contact_id,))
            self.conn.commit()
            
            if cur.rowcount > 0:
                print(f"✓ Contact deleted")
            else:
                print(f"✗ Contact not found")
            cur.close()
        except psycopg2.Error as e:
            self.conn.rollback()
            print(f"✗ Error deleting contact: {e}")

    # ===== Search & Query =====
    
    def search_contacts(self, query):
        """Search contacts by name, email, or phone number."""
        try:
            cur = self.conn.cursor()
            cur.execute("SELECT * FROM search_contacts(%s)", (query,))
            results = cur.fetchall()
            cur.close()
            
            if not results:
                print(f"✗ No contacts found matching '{query}'")
                return
            
            print(f"\n{'ID':<5} {'Name':<20} {'Email':<25} {'Birthday':<12} {'Group':<12} {'Phone':<15} {'Type':<8}")
            print("-" * 105)
            
            for row in results:
                contact_id, name, email, birthday, group_name, phone, phone_type = row
                email_str = email or ""
                birthday_str = birthday.strftime('%Y-%m-%d') if birthday else ""
                group_str = group_name or ""
                phone_str = phone or ""
                type_str = phone_type or ""
                
                print(f"{contact_id:<5} {name:<20} {email_str:<25} {birthday_str:<12} {group_str:<12} {phone_str:<15} {type_str:<8}")
            print()
        except psycopg2.Error as e:
            print(f"✗ Search error: {e}")

    def search_by_email(self, email_query):
        """Search contacts by email (partial match)."""
        try:
            cur = self.conn.cursor()
            cur.execute("""
                SELECT id, name, email, birthday, group_id
                FROM contacts
                WHERE email ILIKE %s
                ORDER BY name
            """, (f"%{email_query}%",))
            
            results = cur.fetchall()
            cur.close()
            
            if not results:
                print(f"✗ No contacts found with email containing '{email_query}'")
                return
            
            print(f"\n{'ID':<5} {'Name':<20} {'Email':<30} {'Birthday':<12}")
            print("-" * 70)
            
            for contact_id, name, email, birthday, _ in results:
                email_str = email or ""
                birthday_str = birthday.strftime('%Y-%m-%d') if birthday else ""
                print(f"{contact_id:<5} {name:<20} {email_str:<30} {birthday_str:<12}")
            print()
        except psycopg2.Error as e:
            print(f"✗ Error searching by email: {e}")

    def filter_by_group(self, group_name):
        """Display all contacts in a specific group."""
        try:
            cur = self.conn.cursor()
            cur.execute("""
                SELECT c.id, c.name, c.email, c.birthday, g.name
                FROM contacts c
                LEFT JOIN groups g ON c.group_id = g.id
                WHERE g.name = %s
                ORDER BY c.name
            """, (group_name,))
            
            results = cur.fetchall()
            cur.close()
            
            if not results:
                print(f"✗ No contacts found in group '{group_name}'")
                return
            
            print(f"\n{'ID':<5} {'Name':<20} {'Email':<30} {'Birthday':<12} {'Group':<12}")
            print("-" * 80)
            
            for contact_id, name, email, birthday, group in results:
                email_str = email or ""
                birthday_str = birthday.strftime('%Y-%m-%d') if birthday else ""
                print(f"{contact_id:<5} {name:<20} {email_str:<30} {birthday_str:<12} {group or '':<12}")
            print()
        except psycopg2.Error as e:
            print(f"✗ Error filtering by group: {e}")

    # ===== Sorting & Pagination =====
    
    def get_all_contacts_sorted(self, sort_by='name'):
        """Get all contacts sorted by name, birthday, or creation date."""
        valid_sorts = {'name': 'c.name', 'birthday': 'c.birthday', 'created': 'c.created_at'}
        
        if sort_by not in valid_sorts:
            print(f"✗ Invalid sort option. Use: {', '.join(valid_sorts.keys())}")
            return
        
        try:
            cur = self.conn.cursor()
            query = f"""
                SELECT c.id, c.name, c.email, c.birthday, g.name, 
                       COUNT(p.id) as phone_count
                FROM contacts c
                LEFT JOIN groups g ON c.group_id = g.id
                LEFT JOIN phones p ON c.id = p.contact_id
                GROUP BY c.id, g.name
                ORDER BY {valid_sorts[sort_by]}
            """
            cur.execute(query)
            results = cur.fetchall()
            cur.close()
            
            if not results:
                print("✗ No contacts found")
                return
            
            print(f"\n{'ID':<5} {'Name':<20} {'Email':<30} {'Birthday':<12} {'Group':<12} {'Phones':<7}")
            print("-" * 90)
            
            for contact_id, name, email, birthday, group, phone_count in results:
                email_str = email or ""
                birthday_str = birthday.strftime('%Y-%m-%d') if birthday else ""
                print(f"{contact_id:<5} {name:<20} {email_str:<30} {birthday_str:<12} {group or '':<12} {phone_count:<7}")
            print()
        except psycopg2.Error as e:
            print(f"✗ Error retrieving contacts: {e}")

    def paginate_contacts(self, page=0):
        """Display contacts with pagination."""
        try:
            cur = self.conn.cursor()
            cur.execute(
                "SELECT * FROM get_contacts_paginated(%s, %s)",
                (page * PAGE_SIZE, PAGE_SIZE)
            )
            
            results = cur.fetchall()
            
            if not results:
                print("✗ No contacts on this page")
                cur.close()
                return
            
            print(f"\n--- Page {page + 1} ---")
            print(f"{'ID':<5} {'Name':<20} {'Email':<30} {'Birthday':<12} {'Group':<12} {'Phones':<7}")
            print("-" * 90)
            
            for contact_id, name, email, birthday, group, phone_count in results:
                email_str = email or ""
                birthday_str = birthday.strftime('%Y-%m-%d') if birthday else ""
                print(f"{contact_id:<5} {name:<20} {email_str:<30} {birthday_str:<12} {group or '':<12} {phone_count:<7}")
            
            self.current_page = page
            print(f"\nNavigate: 'next', 'prev', or enter page number")
            cur.close()
        except psycopg2.Error as e:
            print(f"✗ Error retrieving contacts: {e}")

    def view_contact_details(self, contact_id):
        """View full details of a single contact including all phones."""
        try:
            cur = self.conn.cursor()
            
            # Get contact info
            cur.execute("""
                SELECT c.id, c.name, c.email, c.birthday, g.name, c.created_at
                FROM contacts c
                LEFT JOIN groups g ON c.group_id = g.id
                WHERE c.id = %s
            """, (contact_id,))
            
            contact = cur.fetchone()
            if not contact:
                print(f"✗ Contact not found")
                cur.close()
                return
            
            contact_id, name, email, birthday, group, created_at = contact
            
            # Get all phones
            cur.execute("""
                SELECT id, phone, type FROM phones
                WHERE contact_id = %s
                ORDER BY type
            """, (contact_id,))
            
            phones = cur.fetchall()
            cur.close()
            
            print(f"\n--- Contact Details ---")
            print(f"ID: {contact_id}")
            print(f"Name: {name}")
            print(f"Email: {email or 'N/A'}")
            print(f"Birthday: {birthday.strftime('%Y-%m-%d') if birthday else 'N/A'}")
            print(f"Group: {group or 'N/A'}")
            print(f"Created: {created_at.strftime('%Y-%m-%d %H:%M:%S') if created_at else 'N/A'}")
            
            if phones:
                print(f"\nPhones:")
                for phone_id, phone, phone_type in phones:
                    print(f"  • {phone} ({phone_type})")
            else:
                print(f"\nPhones: None")
            print()
        except psycopg2.Error as e:
            print(f"✗ Error retrieving contact details: {e}")

    # ===== Import/Export =====
    
    def import_csv(self, filename):
        """Import contacts from CSV file."""
        if not os.path.exists(filename):
            print(f"✗ File '{filename}' not found")
            return
        
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                
                for row_num, row in enumerate(reader, start=2):
                    name = row.get('name', '').strip()
                    email = row.get('email', '').strip() or None
                    birthday = row.get('birthday', '').strip() or None
                    group = row.get('group', '').strip() or None
                    phone1 = row.get('phone1', '').strip() or None
                    phone1_type = row.get('phone1_type', 'mobile').strip()
                    phone2 = row.get('phone2', '').strip() or None
                    phone2_type = row.get('phone2_type', 'mobile').strip()
                    
                    if not name:
                        print(f"✗ Row {row_num}: Name is required, skipping")
                        continue
                    
                    # Add contact
                    contact_id = self.add_contact(name, email, birthday, group)
                    
                    # Add phones
                    if contact_id and phone1:
                        self.add_phone(name, phone1, phone1_type)
                    if contact_id and phone2:
                        self.add_phone(name, phone2, phone2_type)
            
            print(f"✓ CSV import completed")
        except Exception as e:
            print(f"✗ Error importing CSV: {e}")

    def export_json(self, filename):
        """Export all contacts to JSON file."""
        try:
            cur = self.conn.cursor()
            
            cur.execute("""
                SELECT c.id, c.name, c.email, c.birthday, g.name
                FROM contacts c
                LEFT JOIN groups g ON c.group_id = g.id
                ORDER BY c.name
            """)
            
            contacts_list = []
            for contact_id, name, email, birthday, group in cur.fetchall():
                # Get phones for this contact
                cur.execute("""
                    SELECT phone, type FROM phones
                    WHERE contact_id = %s
                    ORDER BY type
                """, (contact_id,))
                
                phones = [{'phone': p[0], 'type': p[1]} for p in cur.fetchall()]
                
                contacts_list.append({
                    'id': contact_id,
                    'name': name,
                    'email': email,
                    'birthday': birthday.isoformat() if birthday else None,
                    'group': group,
                    'phones': phones
                })
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(contacts_list, f, indent=2, ensure_ascii=False)
            
            cur.close()
            print(f"✓ Exported {len(contacts_list)} contacts to '{filename}'")
        except Exception as e:
            print(f"✗ Error exporting JSON: {e}")

    def import_json(self, filename):
        """Import contacts from JSON file with duplicate handling."""
        if not os.path.exists(filename):
            print(f"✗ File '{filename}' not found")
            return
        
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                contacts_list = json.load(f)
            
            imported = 0
            skipped = 0
            
            for contact in contacts_list:
                name = contact.get('name', '').strip()
                email = contact.get('email') or None
                birthday = contact.get('birthday') or None
                group = contact.get('group') or None
                phones = contact.get('phones', [])
                
                if not name:
                    skipped += 1
                    continue
                
                # Check if contact exists
                cur = self.conn.cursor()
                cur.execute("SELECT id FROM contacts WHERE name = %s", (name,))
                existing = cur.fetchone()
                cur.close()
                
                if existing:
                    print(f"\nContact '{name}' already exists. (s)kip or (o)verwrite? ", end='')
                    choice = input().lower().strip()
                    if choice != 'o':
                        skipped += 1
                        continue
                    # Update existing
                    self.update_contact(existing[0], name, email, birthday)
                else:
                    # Create new
                    self.add_contact(name, email, birthday, group)
                
                # Add phones
                for phone in phones:
                    self.add_phone(name, phone['phone'], phone.get('type', 'mobile'))
                
                imported += 1
            
            print(f"\n✓ JSON import completed: {imported} imported, {skipped} skipped")
        except Exception as e:
            print(f"✗ Error importing JSON: {e}")

    def move_to_group(self, contact_name, group_name):
        """Move a contact to a different group."""
        try:
            cur = self.conn.cursor()
            cur.execute("CALL move_to_group(%s, %s)", (contact_name, group_name))
            self.conn.commit()
            cur.close()
            print(f"✓ Contact moved to group '{group_name}'")
        except psycopg2.Error as e:
            self.conn.rollback()
            print(f"✗ Error moving contact: {e}")

    def export_csv(self, filename):
        """Export all contacts to CSV file."""
        try:
            cur = self.conn.cursor()
            
            cur.execute("""
                SELECT c.id, c.name, c.email, c.birthday, g.name
                FROM contacts c
                LEFT JOIN groups g ON c.group_id = g.id
                ORDER BY c.name
            """)
            
            contacts_list = []
            for contact_id, name, email, birthday, group in cur.fetchall():
                # Get phones for this contact
                cur.execute("""
                    SELECT phone, type FROM phones
                    WHERE contact_id = %s
                    ORDER BY type
                """, (contact_id,))
                
                phones = cur.fetchall()
                
                # Create row for each phone, or one row if no phones
                if phones:
                    for idx, (phone, phone_type) in enumerate(phones):
                        contacts_list.append({
                            'name': name if idx == 0 else '',
                            'email': email if idx == 0 else '',
                            'birthday': birthday.isoformat() if birthday and idx == 0 else '',
                            'group': group if idx == 0 else '',
                            'phone': phone,
                            'phone_type': phone_type
                        })
                else:
                    contacts_list.append({
                        'name': name,
                        'email': email or '',
                        'birthday': birthday.isoformat() if birthday else '',
                        'group': group or '',
                        'phone': '',
                        'phone_type': ''
                    })
            
            # Write to CSV
            with open(filename, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=['name', 'email', 'birthday', 'group', 'phone', 'phone_type'])
                writer.writeheader()
                writer.writerows(contacts_list)
            
            cur.close()
            print(f"✓ Exported {len(contacts_list)} phone entries to '{filename}'")
        except Exception as e:
            print(f"✗ Error exporting CSV: {e}")

    def list_groups(self):
        """List all available groups."""
        try:
            cur = self.conn.cursor()
            cur.execute("SELECT name, COUNT(c.id) FROM groups g LEFT JOIN contacts c ON g.id = c.group_id GROUP BY g.id, g.name ORDER BY g.name")
            groups = cur.fetchall()
            cur.close()
            
            if not groups:
                print("✗ No groups found")
                return
            
            print(f"\n{'Group':<20} {'Contacts':<10}")
            print("-" * 30)
            for group_name, count in groups:
                print(f"{group_name:<20} {count:<10}")
            print()
        except psycopg2.Error as e:
            print(f"✗ Error listing groups: {e}")


def print_menu():
    """Display main menu."""
    print("""
╔════════════════════════════════════════╗
║        PHONEBOOK APPLICATION           ║
╚════════════════════════════════════════╝

1.  Add contact
2.  View contact details
3.  Update contact
4.  Delete contact
5.  Search by name/email/phone
6.  Search by email
7.  Filter by group
8.  Sort and view all
9.  Paginate contacts
10. Add phone to contact
11. Move contact to group
12. List groups
13. Import from CSV
14. Import from JSON
15. Export to JSON
16. Export to CSV
17. Exit

Enter choice: """)


def main():
    """Main application loop."""
    try:
        pb = PhoneBook()
        print("\n✓ Connected to database\n")
    except Exception as e:
        print(f"✗ Failed to start: {e}")
        return
    
    while True:
        print_menu()
        choice = input().strip()
        
        if choice == '1':
            # Add contact
            name = input("Contact name: ").strip()
            if not name:
                print("✗ Name is required\n")
                continue
            email = input("Email (optional): ").strip() or None
            birthday = input("Birthday YYYY-MM-DD (optional): ").strip() or None
            group = input("Group name (optional): ").strip() or None
            pb.add_contact(name, email, birthday, group)
        
        elif choice == '2':
            # View contact details
            contact_id = input("Enter contact ID: ").strip()
            try:
                pb.view_contact_details(int(contact_id))
            except ValueError:
                print("✗ Invalid contact ID\n")
        
        elif choice == '3':
            # Update contact
            contact_id = input("Enter contact ID: ").strip()
            try:
                contact_id = int(contact_id)
                name = input("New name (press Enter to skip): ").strip() or None
                email = input("New email (press Enter to skip): ").strip() or None
                birthday = input("New birthday YYYY-MM-DD (press Enter to skip): ").strip() or None
                pb.update_contact(contact_id, name, email, birthday)
            except ValueError:
                print("✗ Invalid contact ID\n")
        
        elif choice == '4':
            # Delete contact
            contact_id = input("Enter contact ID: ").strip()
            try:
                pb.delete_contact(int(contact_id))
            except ValueError:
                print("✗ Invalid contact ID\n")
        
        elif choice == '5':
            # Search by name/email/phone
            query = input("Search query: ").strip()
            if query:
                pb.search_contacts(query)
            else:
                print("✗ Search query required\n")
        
        elif choice == '6':
            # Search by email
            query = input("Email search: ").strip()
            if query:
                pb.search_by_email(query)
            else:
                print("✗ Search query required\n")
        
        elif choice == '7':
            # Filter by group
            pb.list_groups()
            group = input("Enter group name: ").strip()
            if group:
                pb.filter_by_group(group)
            else:
                print("✗ Group name required\n")
        
        elif choice == '8':
            # Sort and view
            print("Sort by: (1) name, (2) birthday, (3) created")
            sort_choice = input().strip()
            sort_map = {'1': 'name', '2': 'birthday', '3': 'created'}
            sort_by = sort_map.get(sort_choice, 'name')
            pb.get_all_contacts_sorted(sort_by)
        
        elif choice == '9':
            # Paginate
            pb.paginate_contacts(0)
            while True:
                nav = input().strip().lower()
                if nav == 'next':
                    pb.paginate_contacts(pb.current_page + 1)
                elif nav == 'prev' and pb.current_page > 0:
                    pb.paginate_contacts(pb.current_page - 1)
                elif nav == 'quit':
                    break
                elif nav.isdigit():
                    pb.paginate_contacts(int(nav))
                else:
                    print("✗ Invalid command\n")
        
        elif choice == '10':
            # Add phone
            name = input("Contact name: ").strip()
            phone = input("Phone number: ").strip()
            phone_type = input("Type (home/work/mobile): ").strip()
            if name and phone and phone_type in ['home', 'work', 'mobile']:
                pb.add_phone(name, phone, phone_type)
            else:
                print("✗ Invalid input\n")
        
        elif choice == '11':
            # Move to group
            name = input("Contact name: ").strip()
            group = input("Group name: ").strip()
            if name and group:
                pb.move_to_group(name, group)
            else:
                print("✗ Invalid input\n")
        
        elif choice == '12':
            # List groups
            pb.list_groups()
        
        elif choice == '13':
            # Import CSV
            filename = input("CSV filename: ").strip()
            if filename:
                pb.import_csv(filename)
            else:
                print("✗ Filename required\n")
        
        elif choice == '14':
            # Import JSON
            filename = input("JSON filename: ").strip()
            if filename:
                pb.import_json(filename)
            else:
                print("✗ Filename required\n")
        
        elif choice == '15':
            # Export JSON
            filename = input("Output filename: ").strip()
            if filename:
                pb.export_json(filename)
            else:
                print("✗ Filename required\n")
        
        elif choice == '16':
            # Export CSV
            filename = input("Output filename: ").strip()
            if filename:
                pb.export_csv(filename)
            else:
                print("✗ Filename required\n")
        
        elif choice == '17':
            # Exit
            print("\n✓ Closing application...")
            pb.close()
            break
        
        else:
            print("✗ Invalid choice\n")


if __name__ == '__main__':
    main()
