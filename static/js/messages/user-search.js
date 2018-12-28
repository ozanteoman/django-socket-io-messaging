$(document).ready(function () {
    $("input[name=to]").autocomplete({
        source: function (request, response) {
            const $this = this.element;
            const $val = $this.val().trim();
            if ($val === '') {
                return 1;
            }
            $.ajax({
                url: "/messages/users-search",
                dataType: "json",
                data: {
                    to: $val
                },
                success: function (data) {
                    const new_data = data.users_list;
                    response($.map(new_data, function (item) {
                        return {
                            label: item.username,
                            value: item.username
                        }
                    }))
                }
            });
        },
        minLength: 2,
        select: function (event, ui) {
        }
    })


});