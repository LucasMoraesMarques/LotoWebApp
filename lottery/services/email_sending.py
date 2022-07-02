from django.core.mail import send_mail, get_connection, EmailMultiAlternatives
from django.template.loader import get_template
from LotoWebApp import settings
from django.core.files.storage import default_storage


def custom_send_email(emails_info):
    with get_connection() as connection:
        emails = []
        for user, emails_info in emails_info.items():
            for email_info in emails_info:
                if email_info["FILES"]:
                    template = get_template(email_info["TEMPLATE"])
                    ctx = {"user": user}
                    html = template.render(ctx)

                    email = EmailMultiAlternatives(
                        email_info["SUBJECT"],
                        email_info["BODY"],
                        email_info["FROM"],
                        to=email_info["TO"],
                        bcc=[settings.ADMINS],
                        connection=connection,
                    )
                    email.attach_alternative(html, "text/html")
                    for file in email_info["FILES"]:
                        file_name = str(file.name).split("/")[-1]
                        file_extension = file_name.split(".")[-1]
                        mime_type = get_mime_type(file_extension)
                        email.attach(
                            f"{file_name}",
                            default_storage.open(file.name, "rb").read(),
                            mime_type,
                        )
                    emails.append(email)
        connection.send_messages(emails)


def get_mime_type(file_extension):
    mime_type = "text/plain"
    if file_extension in ["txt", "text"]:
        mime_type = "text/plain"
    elif file_extension == "pdf":
        mime_type = "application/pdf"
    elif file_extension == "xlsx":
        mime_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    elif file_extension == "xls":
        mime_type = "application/vnd.ms-excel"
    return mime_type


def send_games_sets_by_email(email_info):
    with get_connection() as connection:
        template = get_template(email_info["TEMPLATE"])
        ctx = {"user": email_info["USER"]}
        html = template.render(ctx)

        email = EmailMultiAlternatives(
            email_info["SUBJECT"],
            email_info["BODY"],
            email_info["FROM"],
            to=email_info["TO"],
            bcc=[settings.ADMINS],
            connection=connection,
        )
        email.attach_alternative(html, "text/html")
        email.attach(
            email_info["FILE"]["file_name"],
            email_info["FILE"]["output"].read(),
            email_info["FILE"]["content_type"],
        )
        email.send()


