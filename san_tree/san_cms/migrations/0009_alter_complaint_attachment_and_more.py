from django.db import migrations, models

import san_cms.models


class Migration(migrations.Migration):

    dependencies = [
        ("san_cms", "0008_remove_complaint_assigned_to_many"),
    ]

    operations = [
        migrations.AlterField(
            model_name="complaint",
            name="attachment",
            field=models.ImageField(
                blank=True,
                null=True,
                upload_to=san_cms.models.complaint_image_path,
                validators=[san_cms.models.validate_image_size],
            ),
        ),
        migrations.AlterField(
            model_name="complaintremarks",
            name="attachment",
            field=models.ImageField(
                blank=True,
                null=True,
                upload_to=san_cms.models.complaint_remark_image_path,
                validators=[san_cms.models.validate_image_size],
            ),
        ),
    ]
