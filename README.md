# Library Management System (Console App)

A **console-based library management system** in Python that allows managing books, book copies (BookItems), members, checkouts, reservations, fines, and notifications.

---

## Features

- Add and manage **Books** and multiple **BookItems** (copies of a book).  
- Track **BookItem status**: Available, Checked Out, Reserved.  
- Add and manage **Library Members**.  
- Members can:
  - Check out available books (up to 5 at a time).  
  - Return books and automatically calculate fines for overdue returns.  
  - Reserve books that are currently checked out.  
- Automatic **fine calculation** for overdue books.  
- **Notifications** for overdue books and availability of reserved books.  
- Catalog search by **title**, **author**, **subject**, and **publication date**.  
- Library statistics for total books, items, and members.

---

## Classes Overview

### Core Classes
- **Book** – Represents a book with ISBN, title, author, subject, and publication date.  
- **BookItem** – Represents a copy of a book with a unique ID, rack location, status, and borrower info.  
- **Member** – Represents a library member who can check out, return, and reserve books.  
- **Fine** – Represents fines for overdue books.  

### Services
- **Catalog** – Allows searching books by title, author, subject, or publication date.  
- **NotificationService** – Sends notifications to members for overdue or available reserved books.  
- **Library** – Singleton class that manages all books, book items, members, catalog, and notifications.

---

## Installation

1. Clone the repository:

```bash
git clone <repo-url>
cd library-management-system
