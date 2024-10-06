#include <stdio.h>
#include <stdlib.h>
#include <string.h>

typedef struct {
    void* data;
    size_t size;
    int mutable_borrowed;             // 1 = mutably borrowed, 0 = not borrowed mutably
    int immutable_borrow_count;       // Tracks the number of active immutable borrows
    int ref_count;                    // Reference count for automatic memory management
} ManagedObject;

// Create a new object with reference counting initialized to 1
ManagedObject* create_object(size_t size) {
    ManagedObject* obj = (ManagedObject*)malloc(sizeof(ManagedObject));
    obj->data = malloc(size);
    obj->size = size;
    obj->mutable_borrowed = 0;
    obj->immutable_borrow_count = 0;
    obj->ref_count = 1;               // Initial reference count is 1 (owned by creator)
    return obj;
}

// Increase reference count (e.g., when borrowed)
void add_reference(ManagedObject* obj) {
    obj->ref_count++;
}

// Decrease reference count and destroy if zero
void remove_reference(ManagedObject* obj) {
    obj->ref_count--;
    if (obj->ref_count == 0) {
        // Clean up object when no references remain
        free(obj->data);
        free(obj);
    }
}

// Immutable borrow (returns NULL if a mutable borrow is active)
void* borrow_immutable(ManagedObject* obj) {
    if (obj->mutable_borrowed) {
        fprintf(stderr, "Error: Cannot borrow immutably while object is mutably borrowed.\n");
        return NULL;
    }
    obj->immutable_borrow_count++;
    add_reference(obj);  // Increment reference count for the new borrow
    return obj->data;
}

// Mutable borrow (returns NULL if any borrow is active)
void* borrow_mutable(ManagedObject* obj) {
    if (obj->mutable_borrowed || obj->immutable_borrow_count > 0) {
        fprintf(stderr, "Error: Cannot borrow mutably while object is borrowed.\n");
        return NULL;
    }
    obj->mutable_borrowed = 1;
    add_reference(obj);  // Increment reference count for the new borrow
    return obj->data;
}

// Return an object after borrowing (decrease reference count)
void return_object(ManagedObject* obj) {
    if (obj->mutable_borrowed) {
        obj->mutable_borrowed = 0;  // Release mutable borrow
    } else if (obj->immutable_borrow_count > 0) {
        obj->immutable_borrow_count--;  // Decrement immutable borrow count
    }
    remove_reference(obj);  // Decrease reference count when returning the object
}

// Destroy the object (called when reference count reaches 0)
void destroy_object(ManagedObject* obj) {
    remove_reference(obj);  // Decrease reference count and clean up if zero
}

// Debugging: Print the current status of the object
void print_object_status(ManagedObject* obj) {
    printf("Object status:\n");
    printf("  Reference count: %d\n", obj->ref_count);
    printf("  Mutable borrowed: %s\n", obj->mutable_borrowed ? "Yes" : "No");
    printf("  Immutable borrow count: %d\n", obj->immutable_borrow_count);
}

// Check if the object is currently mutably borrowed
int is_mutably_borrowed(ManagedObject* obj) {
    return obj->mutable_borrowed;
}

// Check if the object is currently immutably borrowed
int is_immutably_borrowed(ManagedObject* obj) {
    return obj->immutable_borrow_count > 0;
}

