from memory_manager import MemoryManager

mgr = MemoryManager()

profile = mgr.get_or_create("Alice")

mgr.record_topic(profile, "for loops")
mgr.record_error(
    profile,
    "NameError",
    "name 'x' is not defined",
    "variables"
)
mgr.mark_mastered(profile, "variables")

print(profile.get_summary())