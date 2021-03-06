"""Initial migration

Revision ID: 33200cef9060
Revises: None
Create Date: 2016-05-05 21:12:22.134639

"""

# revision identifiers, used by Alembic.
revision = "33200cef9060"
down_revision = None

from alembic import op  # noqa: E402
import sqlalchemy as sa  # noqa: E402


def upgrade():
    op.create_table(
        "bands",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("modes", sa.String(length=255), nullable=True),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("lower", sa.BigInteger(), nullable=True),
        sa.Column("upper", sa.BigInteger(), nullable=True),
        sa.Column("start", sa.BigInteger(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "cat",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("radio", sa.String(length=250), nullable=False),
        sa.Column("frequency", sa.Integer(), nullable=False),
        sa.Column("mode", sa.String(length=10), nullable=False),
        sa.Column("timestamp", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "config",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("lotw_download_url", sa.String(length=255), nullable=True),
        sa.Column("lotw_upload_url", sa.String(length=255), nullable=True),
        sa.Column("lotw_rcvd_mark", sa.String(length=255), nullable=True),
        sa.Column("lotw_login_url", sa.String(length=255), nullable=True),
        sa.Column("eqsl_download_url", sa.String(length=255), nullable=True),
        sa.Column("eqsl_rcvd_mark", sa.String(length=255), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "contest_template",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("band_160", sa.String(length=20), nullable=False),
        sa.Column("band_80", sa.String(length=20), nullable=False),
        sa.Column("band_40", sa.String(length=20), nullable=False),
        sa.Column("band_20", sa.String(length=20), nullable=False),
        sa.Column("band_15", sa.String(length=20), nullable=False),
        sa.Column("band_10", sa.String(length=20), nullable=False),
        sa.Column("band_6m", sa.String(length=20), nullable=False),
        sa.Column("band_4m", sa.String(length=20), nullable=False),
        sa.Column("band_2m", sa.String(length=20), nullable=False),
        sa.Column("band_70cm", sa.String(length=20), nullable=False),
        sa.Column("band_23cm", sa.String(length=20), nullable=False),
        sa.Column("mode_ssb", sa.String(length=20), nullable=False),
        sa.Column("mode_cw", sa.String(length=20), nullable=False),
        sa.Column("serial", sa.String(length=20), nullable=False),
        sa.Column("point_per_km", sa.String(length=20), nullable=False),
        sa.Column("qra", sa.String(length=20), nullable=False),
        sa.Column("other_exch", sa.String(length=255), nullable=False),
        sa.Column("scoring", sa.String(length=255), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_contest_template_name"), "contest_template", ["name"], unique=False)
    op.create_table(
        "contests",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("start", sa.DateTime(), nullable=False),
        sa.Column("end", sa.DateTime(), nullable=False),
        sa.Column("template", sa.Integer(), nullable=False),
        sa.Column("serial_num", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "dxcc",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("prefix", sa.String(length=30), nullable=False),
        sa.Column("name", sa.String(length=150), nullable=True),
        sa.Column("cqz", sa.Float(), nullable=False),
        sa.Column("ituz", sa.Float(), nullable=False),
        sa.Column("cont", sa.String(length=5), nullable=False),
        sa.Column("long", sa.Float(), nullable=False),
        sa.Column("lat", sa.Float(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_dxcc_prefix"), "dxcc", ["prefix"], unique=False)
    op.create_table(
        "dxccexceptions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("prefix", sa.String(length=30), nullable=False),
        sa.Column("name", sa.String(length=150), nullable=True),
        sa.Column("cqz", sa.Float(), nullable=False),
        sa.Column("ituz", sa.Float(), nullable=False),
        sa.Column("cont", sa.String(length=5), nullable=False),
        sa.Column("long", sa.Float(), nullable=False),
        sa.Column("lat", sa.Float(), nullable=False),
        sa.Column("start", sa.DateTime(), nullable=False),
        sa.Column("end", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_dxccexceptions_prefix"), "dxccexceptions", ["prefix"], unique=False)
    op.create_table(
        "modes",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("mode", sa.String(length=255), nullable=False),
        sa.Column("submode", sa.String(length=255), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "role",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=80), nullable=False),
        sa.Column("description", sa.String(length=255), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )
    op.create_table(
        "user",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("password", sa.String(length=255), nullable=False),
        sa.Column("active", sa.Boolean(), nullable=True),
        sa.Column("confirmed_at", sa.DateTime(), nullable=True),
        sa.Column("callsign", sa.String(length=32), nullable=True),
        sa.Column("locator", sa.String(length=16), nullable=True),
        sa.Column("firstname", sa.String(length=32), nullable=True),
        sa.Column("lastname", sa.String(length=32), nullable=True),
        sa.Column("lotw_name", sa.String(length=32), nullable=True),
        sa.Column("lotw_password", sa.String(length=255), nullable=True),
        sa.Column("eqsl_name", sa.String(length=32), nullable=True),
        sa.Column("eqsl_password", sa.String(length=255), nullable=True),
        sa.Column("timezone", sa.String(length=255), nullable=False),
        sa.Column("swl", sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
        sa.UniqueConstraint("name"),
    )
    op.create_table(
        "apitoken",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("token", sa.String(length=255), nullable=False),
        sa.Column("secret", sa.String(length=255), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["user.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("secret"),
        sa.UniqueConstraint("token"),
    )
    op.create_table(
        "log",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("address", sa.String(length=255), nullable=True),
        sa.Column("age", sa.Integer(), nullable=True),
        sa.Column("a_index", sa.Float(), nullable=True),
        sa.Column("ant_az", sa.Float(), nullable=True),
        sa.Column("ant_el", sa.Float(), nullable=True),
        sa.Column("ant_path", sa.String(length=2), nullable=True),
        sa.Column("arrl_sect", sa.String(length=10), nullable=True),
        sa.Column("band_id", sa.Integer(), nullable=False),
        sa.Column("band_rx", sa.String(length=10), nullable=True),
        sa.Column("biography", sa.Text(), nullable=True),
        sa.Column("call", sa.String(length=32), nullable=True),
        sa.Column("check", sa.String(length=8), nullable=True),
        sa.Column("klass", sa.String(length=8), nullable=True),
        sa.Column("cnty", sa.String(length=32), nullable=True),
        sa.Column("comment", sa.UnicodeText(), nullable=True),
        sa.Column("cont", sa.String(length=6), nullable=True),
        sa.Column("contacted_op", sa.String(length=32), nullable=True),
        sa.Column("contest_id", sa.String(length=32), nullable=True),
        sa.Column("country", sa.String(length=64), nullable=True),
        sa.Column("cqz", sa.Integer(), nullable=True),
        sa.Column("distance", sa.Float(), nullable=True),
        sa.Column("dxcc", sa.String(length=6), nullable=True),
        sa.Column("email", sa.String(length=255), nullable=True),
        sa.Column("eq_call", sa.String(length=32), nullable=True),
        sa.Column("eqsl_qslrdate", sa.DateTime(), nullable=True),
        sa.Column("eqsl_qslsdate", sa.DateTime(), nullable=True),
        sa.Column("eqsl_qsl_rcvd", sa.String(length=2), nullable=True),
        sa.Column("eqsl_qsl_sent", sa.String(length=2), nullable=True),
        sa.Column("eqsl_status", sa.String(length=255), nullable=True),
        sa.Column("force_init", sa.Integer(), nullable=True),
        sa.Column("freq", sa.Integer(), nullable=True),
        sa.Column("freq_rx", sa.Integer(), nullable=True),
        sa.Column("gridsquare", sa.String(length=12), nullable=True),
        sa.Column("heading", sa.Float(), nullable=True),
        sa.Column("iota", sa.String(length=10), nullable=True),
        sa.Column("ituz", sa.Integer(), nullable=True),
        sa.Column("k_index", sa.Float(), nullable=True),
        sa.Column("lat", sa.Float(), nullable=True),
        sa.Column("lon", sa.Float(), nullable=True),
        sa.Column("lotw_qslrdate", sa.DateTime(), nullable=True),
        sa.Column("lotw_qslsdate", sa.DateTime(), nullable=True),
        sa.Column("lotw_qsl_rcvd", sa.String(length=2), nullable=True),
        sa.Column("lotw_qsl_sent", sa.String(length=2), nullable=True),
        sa.Column("lotw_status", sa.String(length=255), nullable=True),
        sa.Column("max_bursts", sa.Integer(), nullable=True),
        sa.Column("mode_id", sa.Integer(), nullable=False),
        sa.Column("ms_shower", sa.String(length=32), nullable=True),
        sa.Column("my_city", sa.String(length=32), nullable=True),
        sa.Column("my_cnty", sa.String(length=32), nullable=True),
        sa.Column("my_country", sa.String(length=64), nullable=True),
        sa.Column("my_cq_zone", sa.Integer(), nullable=True),
        sa.Column("my_gridsquare", sa.String(length=12), nullable=True),
        sa.Column("my_iota", sa.String(length=10), nullable=True),
        sa.Column("my_itu_zone", sa.String(length=11), nullable=True),
        sa.Column("my_lat", sa.Float(), nullable=True),
        sa.Column("my_lon", sa.Float(), nullable=True),
        sa.Column("my_name", sa.String(length=255), nullable=True),
        sa.Column("my_postal_code", sa.String(length=24), nullable=True),
        sa.Column("my_rig", sa.String(length=255), nullable=True),
        sa.Column("my_sig", sa.String(length=32), nullable=True),
        sa.Column("my_sig_info", sa.String(length=64), nullable=True),
        sa.Column("my_state", sa.String(length=32), nullable=True),
        sa.Column("my_street", sa.String(length=64), nullable=True),
        sa.Column("name", sa.String(length=128), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("nr_bursts", sa.Integer(), nullable=True),
        sa.Column("nr_pings", sa.Integer(), nullable=True),
        sa.Column("operator", sa.String(length=32), nullable=True),
        sa.Column("owner_callsign", sa.String(length=32), nullable=True),
        sa.Column("pfx", sa.String(length=32), nullable=True),
        sa.Column("precedence", sa.String(length=32), nullable=True),
        sa.Column("prop_mode", sa.String(length=8), nullable=True),
        sa.Column("public_key", sa.String(length=255), nullable=True),
        sa.Column("qslmsg", sa.String(length=255), nullable=True),
        sa.Column("qslrdate", sa.DateTime(), nullable=True),
        sa.Column("qslsdate", sa.DateTime(), nullable=True),
        sa.Column("qsl_rcvd", sa.String(length=2), nullable=True),
        sa.Column("qsl_rcvd_via", sa.String(length=2), nullable=True),
        sa.Column("qsl_sent", sa.String(length=2), nullable=True),
        sa.Column("qsl_sent_via", sa.String(length=2), nullable=True),
        sa.Column("qsl_via", sa.String(length=64), nullable=True),
        sa.Column("qso_complete", sa.String(length=6), nullable=True),
        sa.Column("qso_random", sa.String(length=11), nullable=True),
        sa.Column("qth", sa.String(length=64), nullable=True),
        sa.Column("rig", sa.String(length=255), nullable=True),
        sa.Column("rst_rcvd", sa.String(length=32), nullable=True),
        sa.Column("rst_sent", sa.String(length=32), nullable=True),
        sa.Column("rx_pwr", sa.Float(), nullable=True),
        sa.Column("sat_mode", sa.String(length=32), nullable=True),
        sa.Column("sat_name", sa.String(length=32), nullable=True),
        sa.Column("sfi", sa.Float(), nullable=True),
        sa.Column("sig", sa.String(length=32), nullable=True),
        sa.Column("sig_info", sa.String(length=64), nullable=True),
        sa.Column("srx", sa.String(length=11), nullable=True),
        sa.Column("srx_string", sa.String(length=32), nullable=True),
        sa.Column("state", sa.String(length=32), nullable=True),
        sa.Column("station_callsign", sa.String(length=32), nullable=True),
        sa.Column("stx", sa.String(length=11), nullable=True),
        sa.Column("stx_info", sa.String(length=32), nullable=True),
        sa.Column("swl", sa.Integer(), nullable=True),
        sa.Column("ten_ten", sa.Integer(), nullable=True),
        sa.Column("time_off", sa.DateTime(), nullable=True),
        sa.Column("time_on", sa.DateTime(), nullable=True),
        sa.Column("tx_pwr", sa.Float(), nullable=True),
        sa.Column("web", sa.String(length=255), nullable=True),
        sa.Column("user_defined_0", sa.String(length=64), nullable=True),
        sa.Column("user_defined_1", sa.String(length=64), nullable=True),
        sa.Column("user_defined_2", sa.String(length=64), nullable=True),
        sa.Column("user_defined_3", sa.String(length=64), nullable=True),
        sa.Column("user_defined_4", sa.String(length=64), nullable=True),
        sa.Column("user_defined_5", sa.String(length=64), nullable=True),
        sa.Column("user_defined_6", sa.String(length=64), nullable=True),
        sa.Column("user_defined_7", sa.String(length=64), nullable=True),
        sa.Column("user_defined_8", sa.String(length=64), nullable=True),
        sa.Column("user_defined_9", sa.String(length=64), nullable=True),
        sa.Column("credit_granted", sa.String(length=64), nullable=True),
        sa.Column("credit_submitted", sa.String(length=64), nullable=True),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["band_id"], ["bands.id"]),
        sa.ForeignKeyConstraint(["mode_id"], ["modes.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["user.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_log_call"), "log", ["call"], unique=False)
    op.create_index(op.f("ix_log_cont"), "log", ["cont"], unique=False)
    op.create_index(op.f("ix_log_dxcc"), "log", ["dxcc"], unique=False)
    op.create_index(op.f("ix_log_iota"), "log", ["iota"], unique=False)
    op.create_index(op.f("ix_log_pfx"), "log", ["pfx"], unique=False)
    op.create_index(op.f("ix_log_sat_mode"), "log", ["sat_mode"], unique=False)
    op.create_index(op.f("ix_log_sat_name"), "log", ["sat_name"], unique=False)
    op.create_index(op.f("ix_log_time_on"), "log", ["time_on"], unique=False)
    op.create_table(
        "notes",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("cat", sa.String(length=255), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("note", sa.Text(), nullable=False),
        sa.Column("timestamp", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=True),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["user.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "roles_users",
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("role_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(["role_id"], ["role.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["user.id"]),
    )


def downgrade():
    op.drop_table("roles_users")
    op.drop_table("notes")
    op.drop_index(op.f("ix_log_time_on"), table_name="log")
    op.drop_index(op.f("ix_log_sat_name"), table_name="log")
    op.drop_index(op.f("ix_log_sat_mode"), table_name="log")
    op.drop_index(op.f("ix_log_pfx"), table_name="log")
    op.drop_index(op.f("ix_log_iota"), table_name="log")
    op.drop_index(op.f("ix_log_dxcc"), table_name="log")
    op.drop_index(op.f("ix_log_cont"), table_name="log")
    op.drop_index(op.f("ix_log_call"), table_name="log")
    op.drop_table("log")
    op.drop_table("apitoken")
    op.drop_table("user")
    op.drop_table("role")
    op.drop_table("modes")
    op.drop_index(op.f("ix_dxccexceptions_prefix"), table_name="dxccexceptions")
    op.drop_table("dxccexceptions")
    op.drop_index(op.f("ix_dxcc_prefix"), table_name="dxcc")
    op.drop_table("dxcc")
    op.drop_table("contests")
    op.drop_index(op.f("ix_contest_template_name"), table_name="contest_template")
    op.drop_table("contest_template")
    op.drop_table("config")
    op.drop_table("cat")
    op.drop_table("bands")
