
document.querySelectorAll(".work-page").forEach(function (page) {
    var search = page.querySelector("[data-work-search]");
    var status = page.querySelector("[data-work-status]");
    var priority = page.querySelector("[data-work-priority]");
    var items = Array.from(page.querySelectorAll("[data-work-item]"));
    var resultCount = page.querySelector("[data-result-count]");
    var noMatches = page.querySelector("[data-no-matches]");

    function updateItems() {
        var query = search.value.trim().toLowerCase();
        var statusFilter = status.value;
        var priorityFilter = priority ? priority.value : "all";
        var visibleCount = 0;

        items.forEach(function (item) {
            var matches = item.dataset.search.toLowerCase().includes(query)
                && (statusFilter === "all" || item.dataset.status === statusFilter)
                && (priorityFilter === "all" || item.dataset.priority === priorityFilter);

            item.hidden = !matches;
            if (matches) visibleCount += 1;
        });

        if (resultCount) resultCount.textContent = String(visibleCount);
        if (noMatches) noMatches.hidden = visibleCount > 0;
    }

    if (search && status) {
        search.addEventListener("input", updateItems);
        status.addEventListener("change", updateItems);
        if (priority) priority.addEventListener("change", updateItems);
    }
});
