"""initial schema

Revision ID: 0001
Revises:
Create Date: 2026-07-22
"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql as pg

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"')

    # ---------- countries / cities ----------
    op.create_table(
        "countries",
        sa.Column("id", pg.UUID(as_uuid=True), primary_key=True),
        sa.Column("name_ar", sa.String(100), nullable=False),
        sa.Column("name_en", sa.String(100), nullable=False),
        sa.Column("iso_code", sa.String(2), unique=True, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_table(
        "cities",
        sa.Column("id", pg.UUID(as_uuid=True), primary_key=True),
        sa.Column("country_id", pg.UUID(as_uuid=True), sa.ForeignKey("countries.id"), nullable=False),
        sa.Column("name_ar", sa.String(100), nullable=False),
        sa.Column("name_en", sa.String(100), nullable=False),
        sa.Column("is_active", sa.Boolean, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # ---------- categories ----------
    op.create_table(
        "categories",
        sa.Column("id", pg.UUID(as_uuid=True), primary_key=True),
        sa.Column("parent_id", pg.UUID(as_uuid=True), sa.ForeignKey("categories.id"), nullable=True),
        sa.Column("name_ar", sa.String(100), nullable=False),
        sa.Column("name_en", sa.String(100), nullable=False),
        sa.Column("slug", sa.String(120), unique=True, nullable=False),
        sa.Column("icon_url", sa.String(500)),
        sa.Column("attributes_schema", pg.JSONB, server_default="{}"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # ---------- users ----------
    op.create_table(
        "users",
        sa.Column("id", pg.UUID(as_uuid=True), primary_key=True),
        sa.Column("email", sa.String(255), unique=True, nullable=False),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("full_name", sa.String(150), nullable=False),
        sa.Column("phone", sa.String(30)),
        sa.Column("avatar_url", sa.String(500)),
        sa.Column("city_id", pg.UUID(as_uuid=True), sa.ForeignKey("cities.id")),
        sa.Column("role", sa.String(20), server_default="user"),
        sa.Column("rating_avg", sa.Numeric(2, 1), server_default="0"),
        sa.Column("rating_count", sa.Integer, server_default="0"),
        sa.Column("is_verified", sa.Boolean, server_default=sa.false()),
        sa.Column("is_banned", sa.Boolean, server_default=sa.false()),
        sa.Column("last_login_at", sa.DateTime(timezone=True)),
        sa.Column("last_seen_at", sa.DateTime(timezone=True)),
        sa.Column("push_token", sa.String(500)),
        sa.Column("preferred_language", sa.String(5), server_default="ar"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("deleted_at", sa.DateTime(timezone=True)),
    )
    op.create_index("ix_users_email", "users", ["email"])

    # ---------- listings ----------
    op.create_table(
        "listings",
        sa.Column("id", pg.UUID(as_uuid=True), primary_key=True),
        sa.Column("seller_id", pg.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("category_id", pg.UUID(as_uuid=True), sa.ForeignKey("categories.id"), nullable=True),
        sa.Column("city_id", pg.UUID(as_uuid=True), sa.ForeignKey("cities.id")),
        sa.Column("title", sa.String(200), nullable=False),
        sa.Column("description", sa.Text),
        sa.Column("price", sa.Numeric(12, 2)),
        sa.Column("currency", sa.String(3), server_default="AUD"),
        sa.Column("condition", sa.String(30)),
        sa.Column("status", sa.String(20), server_default="draft"),
        sa.Column("attributes", pg.JSONB, server_default="{}"),
        sa.Column("search_vector", pg.TSVECTOR),
        sa.Column("view_count", sa.Integer, server_default="0"),
        sa.Column("is_ai_generated", sa.Boolean, server_default=sa.false()),
        sa.Column("published_at", sa.DateTime(timezone=True)),
        sa.Column("sold_at", sa.DateTime(timezone=True)),
        sa.Column("expires_at", sa.DateTime(timezone=True)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("deleted_at", sa.DateTime(timezone=True)),
    )
    op.create_index("ix_listings_seller_id", "listings", ["seller_id"])
    op.create_index("ix_listings_status", "listings", ["status"])
    op.create_index("ix_listings_category_id", "listings", ["category_id"])
    op.create_index("ix_listings_city_id", "listings", ["city_id"])
    op.execute("CREATE INDEX ix_listings_search_vector ON listings USING GIN(search_vector)")
    op.execute("CREATE INDEX ix_listings_attributes ON listings USING GIN(attributes)")

    # trigger: يحدث search_vector تلقائياً من title + description بكل INSERT/UPDATE
    op.execute("""
        CREATE FUNCTION listings_search_vector_update() RETURNS trigger AS $$
        BEGIN
          NEW.search_vector :=
            setweight(to_tsvector('simple', coalesce(NEW.title, '')), 'A') ||
            setweight(to_tsvector('simple', coalesce(NEW.description, '')), 'B');
          RETURN NEW;
        END
        $$ LANGUAGE plpgsql;
    """)
    op.execute("""
        CREATE TRIGGER trg_listings_search_vector
        BEFORE INSERT OR UPDATE OF title, description ON listings
        FOR EACH ROW EXECUTE FUNCTION listings_search_vector_update();
    """)

    # ---------- listing_images ----------
    op.create_table(
        "listing_images",
        sa.Column("id", pg.UUID(as_uuid=True), primary_key=True),
        sa.Column("listing_id", pg.UUID(as_uuid=True), sa.ForeignKey("listings.id", ondelete="CASCADE"), nullable=False),
        sa.Column("original_url", sa.String(500), nullable=False),
        sa.Column("thumbnail_url", sa.String(500)),
        sa.Column("optimized_url", sa.String(500)),
        sa.Column("is_enhanced", sa.Boolean, server_default=sa.false()),
        sa.Column("sort_order", sa.Integer, server_default="0"),
        sa.Column("width", sa.Integer),
        sa.Column("height", sa.Integer),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_listing_images_listing_id", "listing_images", ["listing_id"])

    # ---------- listing_ai_metadata ----------
    op.create_table(
        "listing_ai_metadata",
        sa.Column("id", pg.UUID(as_uuid=True), primary_key=True),
        sa.Column("listing_id", pg.UUID(as_uuid=True), sa.ForeignKey("listings.id", ondelete="CASCADE"), unique=True, nullable=False),
        sa.Column("detected_brand", sa.String(100)),
        sa.Column("detected_color", sa.String(50)),
        sa.Column("suggested_price_min", sa.Numeric(12, 2)),
        sa.Column("suggested_price_max", sa.Numeric(12, 2)),
        sa.Column("ai_confidence", sa.Numeric(3, 2)),
        sa.Column("raw_ai_response", pg.JSONB),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # ---------- conversations / messages ----------
    op.create_table(
        "conversations",
        sa.Column("id", pg.UUID(as_uuid=True), primary_key=True),
        sa.Column("listing_id", pg.UUID(as_uuid=True), sa.ForeignKey("listings.id"), nullable=False),
        sa.Column("buyer_id", pg.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("seller_id", pg.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("last_message_preview", sa.String(200)),
        sa.Column("last_message_at", sa.DateTime(timezone=True)),
        sa.Column("last_message_sender_id", pg.UUID(as_uuid=True)),
        sa.Column("buyer_unread_count", sa.Integer, server_default="0"),
        sa.Column("seller_unread_count", sa.Integer, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.UniqueConstraint("listing_id", "buyer_id", "seller_id", name="uq_conversation_participants"),
    )
    op.create_index("ix_conversations_buyer_id", "conversations", ["buyer_id"])
    op.create_index("ix_conversations_seller_id", "conversations", ["seller_id"])

    op.create_table(
        "messages",
        sa.Column("id", pg.UUID(as_uuid=True), primary_key=True),
        sa.Column("conversation_id", pg.UUID(as_uuid=True), sa.ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("sender_id", pg.UUID(as_uuid=True), sa.ForeignKey("users.id")),
        sa.Column("message_type", sa.String(20), server_default="text"),
        sa.Column("content", sa.Text),
        sa.Column("attachments", pg.JSONB),
        sa.Column("is_read", sa.Boolean, server_default=sa.false()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_messages_conversation_id", "messages", ["conversation_id"])

    # ---------- favorites ----------
    op.create_table(
        "favorites",
        sa.Column("id", pg.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", pg.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("listing_id", pg.UUID(as_uuid=True), sa.ForeignKey("listings.id"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.UniqueConstraint("user_id", "listing_id", name="uq_favorite_user_listing"),
    )


def downgrade() -> None:
    op.drop_table("favorites")
    op.drop_table("messages")
    op.drop_table("conversations")
    op.drop_table("listing_ai_metadata")
    op.drop_table("listing_images")
    op.execute("DROP TRIGGER IF EXISTS trg_listings_search_vector ON listings")
    op.execute("DROP FUNCTION IF EXISTS listings_search_vector_update")
    op.drop_table("listings")
    op.drop_table("users")
    op.drop_table("categories")
    op.drop_table("cities")
    op.drop_table("countries")
