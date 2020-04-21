"""Callback handler for poll styling."""
from pollbot.i18n import i18n
from pollbot.helper.poll import poll_required
from pollbot.helper.enums import OptionSorting, UserSorting
from pollbot.helper.update import update_poll_messages
from pollbot.display.poll.compilation import get_poll_text
from pollbot.telegram.keyboard import (
    get_styling_settings_keyboard,
    get_manual_option_order_keyboard,
)


def send_styling_message(session, context):
    """Update the current styling menu message."""
    context.query.message.edit_text(
        text=get_poll_text(session, context.poll),
        parse_mode="markdown",
        reply_markup=get_styling_settings_keyboard(context.poll),
        disable_web_page_preview=True,
    )


@poll_required
def toggle_percentage(session, context, poll):
    """Toggle the visibility of the percentage bar."""
    if poll.anonymous and not poll.show_option_votes:
        context.query.message.chat.send_message(
            text=i18n.t("settings.anonymity_warning", locale=context.user.locale),
        )
        return
    poll.show_percentage = not poll.show_percentage

    session.commit()
    update_poll_messages(session, context.bot, poll)
    send_styling_message(session, context)


@poll_required
def toggle_option_votes(session, context, poll):
    """Toggle the visibility of the vote overview on an option."""
    if poll.anonymous and not poll.show_percentage:
        context.query.message.chat.send_message(
            text=i18n.t("settings.anonymity_warning", locale=context.user.locale),
        )
        return

    poll.show_option_votes = not poll.show_option_votes

    session.commit()
    update_poll_messages(session, context.bot, poll)
    send_styling_message(session, context)


@poll_required
def toggle_date_format(session, context, poll):
    """Switch between european and US date format."""
    poll.european_date_format = not poll.european_date_format
    poll.user.european_date_format = poll.european_date_format

    session.commit()
    update_poll_messages(session, context.bot, poll)
    send_styling_message(session, context)


@poll_required
def toggle_summerization(session, context, poll):
    """Toggle summarization of votes of a poll."""
    poll.summarize = not poll.summarize

    session.commit()
    update_poll_messages(session, context.bot, poll)
    send_styling_message(session, context)


@poll_required
def toggle_compact_buttons(session, context, poll):
    """Toggle the doodle poll button style."""
    poll.compact_buttons = not poll.compact_buttons

    session.commit()
    update_poll_messages(session, context.bot, poll)
    send_styling_message(session, context)


@poll_required
def set_option_order(session, context, poll):
    """Set the order in which options are listed."""
    option_sorting = OptionSorting(context.action)
    poll.option_sorting = option_sorting.name

    session.commit()
    update_poll_messages(session, context.bot, poll)
    send_styling_message(session, context)


@poll_required
def set_user_order(session, context, poll):
    """Set the order in which user are listed."""
    user_sorting = UserSorting(context.action)
    poll.user_sorting = user_sorting.name

    session.commit()
    update_poll_messages(session, context.bot, poll)
    send_styling_message(session, context)


# Manual option order menu
def send_option_order_message(session, context):
    """Update the current styling menu message."""
    context.query.message.edit_text(
        text=get_poll_text(session, context.poll),
        parse_mode="markdown",
        reply_markup=get_manual_option_order_keyboard(context.poll),
        disable_web_page_preview=True,
    )

@poll_required
def open_option_order_menu(session, context, poll):
    """Open the menu for manually adjusting the option order."""
    send_option_order_message(session, context)


@poll_required
def increase_option_index(session, context, poll):
    """Increase the index of a specific option."""
    option_id = context.action

    target_option = None
    for option in poll.options:
        # Find the option we're looking for
        if option.id == option_id:
            target_option = option

            continue

        # Switch index with the next option
        if target_option is not None:
            target_index = option.index
            current_index = target_option.index

            # Change indices to allow changing the index
            # In combination with unique constraints
            # This also acts as a lock, which prevents other
            # requests to change order at the same time
            option.index = -1
            target_option.index = -2
            session.commit()

            # Upate indices
            target_option.index = target_index
            option.index = current_index
            session.commit()

            break

    update_poll_messages(session, context.bot, poll)
    send_option_order_message(session, context)


@poll_required
def decrease_option_index(session, context, poll):
    """Decrease the index of a specific option."""
    option_id = context.action

    prev_option = None
    for option in poll.options:
        # Find the option we're looking for
        if option.id == option_id:
            if prev_option is None:
                return

            # Switch index with the previous option
            current_index = option.index
            target_index = prev_option.index

            # Change indices to allow changing the index
            # In combination with unique constraints
            # This also acts as a lock, which prevents other
            # requests to change order at the same time
            option.index = -2
            prev_option.index = -1
            session.commit()

            # Upate indices
            prev_option.index = current_index
            option.index = target_index
            session.commit()

            break

        prev_option = option

    update_poll_messages(session, context.bot, poll)
    send_option_order_message(session, context)
