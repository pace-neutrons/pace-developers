# Quick script to fix links
# J. Wilkins Nov 2020

:loop;
/\.rst/ {
    /\.rst#\w+>/b subref;
    s/(`[^<]+?<)(\w+)\.rst>`__/:ref:\1\2:\2>`/g;
    :fix
    s/:([A-Za-z0-9_ ]+)_([A-Za-z0-9_ ]+>)/:\1 \2/
    /:[A-Za-z0-9_ ]+_[A-Za-z0-9_ ]+>/{
	b fix # Underscores
    }
    b endblock;
    :subref
    s/(`[^<]+?<)(\w+)\.rst#(\w+)>`__/:ref:\1\2:\3>`/g;
    :endblock
    # Print for debug
    # p
}
/\.rst/b loop;
