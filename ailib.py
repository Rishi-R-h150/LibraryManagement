from enum import Enum
from datetime import date, timedelta
from typing import List, Optional, Dict

# Enums for status
class BookStatus(Enum):
    AVAILABLE = "available"
    CHECKED_OUT = "checked_out"
    RESERVED = "reserved"

# Book class
class Book:
    def __init__(self, isbn: str, title: str, author: str, subject: str, publication_date: date):
        self.isbn = isbn
        self.title = title
        self.author = author
        self.subject = subject
        self.publication_date = publication_date
    
    def get_details(self) -> Dict:
        return {
            "isbn": self.isbn,
            "title": self.title,
            "author": self.author,
            "subject": self.subject,
            "publication_date": self.publication_date
        }

# BookItem class
class BookItem:
    def __init__(self, item_id: str, book: Book, rack_number: str):
        self.item_id = item_id
        self.book = book
        self.rack_number = rack_number
        self.status = BookStatus.AVAILABLE
        self.due_date: Optional[date] = None
        self.borrower: Optional['Member'] = None
        self.borrowed_date: Optional[date] = None
        self.reserved_by: Optional['Member'] = None
    
    def is_available(self) -> bool:
        return self.status == BookStatus.AVAILABLE and self.reserved_by is None
    
    def check_out(self, member: 'Member', checkout_date: date = None, loan_period_days: int = 14) -> bool:
        if checkout_date is None:
            checkout_date = date.today()
            
        # Check if book is available and member hasn't exceeded checkout limit
        if not self.is_available():
            return False
            
        if len(member.checked_out_books) >= 5:
            print(f"Member {member.name} has reached the maximum checkout limit of 5 books")
            return False
        
        # If book is reserved, check if it's reserved by the same member
        if self.reserved_by and self.reserved_by != member:
            return False
            
        # Perform checkout
        self.status = BookStatus.CHECKED_OUT
        self.borrower = member
        self.borrowed_date = checkout_date
        self.due_date = checkout_date + timedelta(days=loan_period_days)
        self.reserved_by = None  # Clear reservation
        
        member.checked_out_books.append(self)
        if self in member.reserved_books:
            member.reserved_books.remove(self)
            
        return True
    
    def return_book(self, return_date: date = None) -> bool:
        
        if return_date is None:
            return_date = date.today()
            
        if self.status != BookStatus.CHECKED_OUT or not self.borrower:
            return False
            
        # Remove from member's checked out books
        if self in self.borrower.checked_out_books:
            self.borrower.checked_out_books.remove(self)
        
        # Reset book item status
       
        #self.borrower.fines.append(Fine.calculate_fine(return_date - self.borrowed_date , 10))
        self.status = BookStatus.AVAILABLE
        self.borrower = None
        self.borrowed_date = None
        self.due_date = None
        
        return True
    
    def reserve(self, member: 'Member') -> bool:
        if self.reserved_by:
            print("Book is already reserved by another member")
            return False
            
        if self.borrower == member:
            print("You cannot reserve a book you've already checked out")
            return False
        
        if self.status == BookStatus.AVAILABLE:
            self.reserved_by = member
            member.reserved_books.append(self)
            return True
            
        return False

# Fine class
class Fine:
    def __init__(self, member: 'Member', book_item: BookItem, amount: float, date_issued: date):
        self.member = member
        self.book_item = book_item
        self.amount = amount
        self.date_issued = date_issued
        self.paid = False
    
    @staticmethod
    def calculate_fine(days_overdue: int, fine_rate: float) -> float:
        return days_overdue * fine_rate if days_overdue > 0 else 0.0

# Member class
class Member:
    def __init__(self, member_id: str, name: str, address: str):
        self.member_id = member_id
        self.name = name
        self.address = address
        self.checked_out_books: List[BookItem] = []
        self.reserved_books: List[BookItem] = []
        self.fines: List[Fine] = []
    
    def check_out_book(self, book_item: BookItem) -> bool:
        return book_item.check_out(self)
    
    def return_book(self, book_item: BookItem) -> bool:
        
        return book_item.return_book()
    
    def reserve_book(self, book_item: BookItem) -> bool:
        return book_item.reserve(self)
    
    def get_fines(self) -> List[Fine]:
        return [fine for fine in self.fines if not fine.paid]
    
    def get_total_fine_amount(self) -> float:
        return sum(fine.amount for fine in self.get_fines())
    
    def receive_notification(self, message: str):
        print(f"Notification for {self.name}: {message}")

# Catalog class
class Catalog:
    def __init__(self):
        self.books: List[Book] = []
    
    def add_book(self, book: Book):
        self.books.append(book)
    
    def search_by_title(self, title: str) -> List[Book]:
        return [book for book in self.books if title.lower() in book.title.lower()]
    
    def search_by_author(self, author: str) -> List[Book]:
        return [book for book in self.books if author.lower() in book.author.lower()]
    
    def search_by_subject(self, subject: str) -> List[Book]:
        return [book for book in self.books if subject.lower() in book.subject.lower()]
    
    def search_by_publication_date(self, publication_date: date) -> List[Book]:
        return [book for book in self.books if book.publication_date == publication_date]

# Notification Service
class NotificationService:
    @staticmethod
    def notify_availability(member: Member, book_item: BookItem):
        message = f"The book '{book_item.book.title}' you reserved is now available for checkout."
        member.receive_notification(message)
    
    @staticmethod
    def notify_overdue(member: Member, book_item: BookItem):
        days_overdue = (date.today() - book_item.due_date).days
        message = f"The book '{book_item.book.title}' is {days_overdue} days overdue. Please return it to avoid additional fines."
        member.receive_notification(message)

# Library class (Singleton pattern)
class Library:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Library, cls).__new__(cls)
            cls._instance.initialized = False
        return cls._instance
    
    def __init__(self):
        if not self.initialized:
            self.books: List[Book] = []
            self.book_items: List[BookItem] = []
            self.members: List[Member] = []
            self.catalog = Catalog()
            self.notification_service = NotificationService()
            self.fine_rate_per_day = 0.50  # $0.50 per day
            self.initialized = True
    
    @staticmethod
    def get_instance():
        return Library()
    
    def add_book(self, book: Book):
        self.books.append(book)
        self.catalog.add_book(book)
    
    def add_book_item(self, book_item: BookItem):
        self.book_items.append(book_item)
    
    def add_member(self, member: Member):
        self.members.append(member)
    
    def find_book_item_by_id(self, item_id: str) -> Optional[BookItem]:
        return next((item for item in self.book_items if item.item_id == item_id), None)
    
    def find_member_by_id(self, member_id: str) -> Optional[Member]:
        return next((member for member in self.members if member.member_id == member_id), None)
    
    def calculate_fine(self, book_item: BookItem, return_date: date = None) -> Optional[Fine]:
        if return_date is None:
            return_date = date.today()
            
        if not book_item.due_date or return_date <= book_item.due_date:
            return None
            
        days_overdue = (return_date - book_item.due_date).days
        fine_amount = Fine.calculate_fine(days_overdue, self.fine_rate_per_day)
        
        if fine_amount > 0:
            fine = Fine(book_item.borrower, book_item, fine_amount, return_date)
            book_item.borrower.fines.append(fine)
            return fine
            
        return None
    
    def send_overdue_notifications(self):
        today = date.today()
        for book_item in self.book_items:
            if (book_item.status == BookStatus.CHECKED_OUT and 
                book_item.due_date and 
                today > book_item.due_date and 
                book_item.borrower):
                self.notification_service.notify_overdue(book_item.borrower, book_item)
    
    def get_available_book_items(self, book: Book) -> List[BookItem]:
        return [item for item in self.book_items 
                if item.book == book and item.is_available()]
    
    def display_library_stats(self):
        print("\n=== Library Statistics ===")
        print(f"Total Books: {len(self.books)}")
        print(f"Total Book Items: {len(self.book_items)}")
        print(f"Total Members: {len(self.members)}")
        
        available_items = sum(1 for item in self.book_items if item.is_available())
        checked_out_items = sum(1 for item in self.book_items if item.status == BookStatus.CHECKED_OUT)
        reserved_items = sum(1 for item in self.book_items if item.reserved_by is not None)
        
        print(f"Available Items: {available_items}")
        print(f"Checked Out Items: {checked_out_items}")
        print(f"Reserved Items: {reserved_items}")

# Example usage and testing
if __name__ == "__main__":
    # Create library instance
    library = Library.get_instance()
    
    # Create some books
    book1 = Book("978-0134685991", "Effective Java", "Joshua Bloch", "Programming", date(2017, 12, 27))
    book2 = Book("978-0135166307", "Clean Code", "Robert Martin", "Programming", date(2008, 8, 1))
    book3 = Book("978-0201633610", "Design Patterns", "Gang of Four", "Programming", date(1994, 10, 31))
    
    # Add books to library
    library.add_book(book1)
    library.add_book(book2)
    library.add_book(book3)
    
    # Create book items
    item1 = BookItem("ITEM001", book1, "A1-001")
    item2 = BookItem("ITEM002", book1, "A1-002")  # Second copy of Effective Java
    item3 = BookItem("ITEM003", book2, "A2-001")
    item4 = BookItem("ITEM004", book3, "A3-001")
    
    # Add book items to library
    library.add_book_item(item1)
    library.add_book_item(item2)
    library.add_book_item(item3)
    library.add_book_item(item4)
    
    # Create members
    member1 = Member("MEM001", "Alice Johnson", "123 Main St")
    member2 = Member("MEM002", "Bob Smith", "456 Oak Ave")
    
    # Add members to library
    library.add_member(member1)
    library.add_member(member2)
    
    # Test catalog search
    print("=== Search Results ===")
    java_books = library.catalog.search_by_title("Java")
    print(f"Books with 'Java' in title: {[book.title for book in java_books]}")
    
    programming_books = library.catalog.search_by_subject("Programming")
    print(f"Programming books: {[book.title for book in programming_books]}")
    
    # Test checkout process
    print("\n=== Checkout Process ===")
    if member1.check_out_book(item1):
        print(f"Successfully checked out '{item1.book.title}' to {member1.name}")
    
    if member2.reserve_book(item1):
        print(f"Successfully reserved '{item1.book.title}' for {member2.name}")
    
    # Display library statistics
    library.display_library_stats()
    
    # Test return process
    print("\n=== Return Process ===")
    if member1.return_book(item1):
        print(f"Successfully returned '{item1.book.title}' from {member1.name}")
        # Notify reserved member that book is available
        if item1.book and member2 in [member for member in library.members if item1 in member.reserved_books]:
            library.notification_service.notify_availability(member2, item1)