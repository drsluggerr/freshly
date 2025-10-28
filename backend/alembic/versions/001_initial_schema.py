"""initial schema

Revision ID: 001
Revises:
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create households table
    op.create_table(
        'households',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )

    # Create users table
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('username', sa.String(), nullable=False),
        sa.Column('hashed_password', sa.String(), nullable=False),
        sa.Column('full_name', sa.String(), nullable=True),
        sa.Column('is_active', sa.Boolean(), server_default=sa.text('true'), nullable=True),
        sa.Column('is_superuser', sa.Boolean(), server_default=sa.text('false'), nullable=True),
        sa.Column('role', sa.Enum('ADMIN', 'EDITOR', 'VIEWER', name='userrole'), nullable=True),
        sa.Column('household_id', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['household_id'], ['households.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_users_username'), 'users', ['username'], unique=True)

    # Create storage_locations table
    op.create_table(
        'storage_locations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('household_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('zone', sa.String(), nullable=True),
        sa.Column('icon', sa.String(), nullable=True),
        sa.Column('color', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['household_id'], ['households.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create products table
    op.create_table(
        'products',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('category', sa.Enum('produce', 'dairy', 'meat', 'seafood', 'bakery', 'frozen', 'canned', 'dry_goods', 'beverages', 'snacks', 'condiments', 'spices', 'other', name='itemcategory'), nullable=False),
        sa.Column('barcode', sa.String(), nullable=True),
        sa.Column('brand', sa.String(), nullable=True),
        sa.Column('default_unit', sa.Enum('oz', 'lb', 'g', 'kg', 'fl_oz', 'cup', 'ml', 'L', 'item', 'serving', name='unittype'), nullable=True),
        sa.Column('average_shelf_life_days', sa.Integer(), nullable=True),
        sa.Column('image_url', sa.String(), nullable=True),
        sa.Column('average_price', sa.Float(), nullable=True),
        sa.Column('last_price', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_products_barcode'), 'products', ['barcode'], unique=True)
    op.create_index(op.f('ix_products_name'), 'products', ['name'], unique=False)

    # Create receipts table
    op.create_table(
        'receipts',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('uploaded_by_id', sa.Integer(), nullable=False),
        sa.Column('household_id', sa.Integer(), nullable=True),
        sa.Column('merchant_name', sa.String(), nullable=True),
        sa.Column('merchant_address', sa.String(), nullable=True),
        sa.Column('purchase_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('total_amount', sa.Float(), nullable=True),
        sa.Column('tax_amount', sa.Float(), nullable=True),
        sa.Column('currency', sa.String(), server_default='USD', nullable=True),
        sa.Column('receipt_number', sa.String(), nullable=True),
        sa.Column('payment_method', sa.String(), nullable=True),
        sa.Column('image_url', sa.String(), nullable=True),
        sa.Column('image_path', sa.String(), nullable=True),
        sa.Column('ocr_provider', sa.String(), nullable=True),
        sa.Column('ocr_raw_response', sa.JSON(), nullable=True),
        sa.Column('processing_time_ms', sa.Integer(), nullable=True),
        sa.Column('processing_status', sa.String(), server_default='pending', nullable=True),
        sa.Column('processing_error', sa.Text(), nullable=True),
        sa.Column('is_duplicate', sa.Boolean(), server_default=sa.text('false'), nullable=True),
        sa.Column('duplicate_of_id', sa.Integer(), nullable=True),
        sa.Column('is_processed', sa.Boolean(), server_default=sa.text('false'), nullable=True),
        sa.Column('items_added', sa.Boolean(), server_default=sa.text('false'), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['duplicate_of_id'], ['receipts.id'], ),
        sa.ForeignKeyConstraint(['household_id'], ['households.id'], ),
        sa.ForeignKeyConstraint(['uploaded_by_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_receipts_receipt_number'), 'receipts', ['receipt_number'], unique=False)

    # Create receipt_line_items table
    op.create_table(
        'receipt_line_items',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('receipt_id', sa.Integer(), nullable=False),
        sa.Column('description', sa.String(), nullable=False),
        sa.Column('quantity', sa.Float(), server_default='1.0', nullable=True),
        sa.Column('unit_price', sa.Float(), nullable=True),
        sa.Column('total_price', sa.Float(), nullable=True),
        sa.Column('matched_product_id', sa.Integer(), nullable=True),
        sa.Column('confidence_score', sa.Float(), nullable=True),
        sa.Column('user_corrected_name', sa.String(), nullable=True),
        sa.Column('category', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['matched_product_id'], ['products.id'], ),
        sa.ForeignKeyConstraint(['receipt_id'], ['receipts.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create inventory_items table
    op.create_table(
        'inventory_items',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('category', sa.Enum('produce', 'dairy', 'meat', 'seafood', 'bakery', 'frozen', 'canned', 'dry_goods', 'beverages', 'snacks', 'condiments', 'spices', 'other', name='itemcategory'), nullable=False),
        sa.Column('barcode', sa.String(), nullable=True),
        sa.Column('quantity', sa.Float(), nullable=False),
        sa.Column('unit', sa.Enum('oz', 'lb', 'g', 'kg', 'fl_oz', 'cup', 'ml', 'L', 'item', 'serving', name='unittype'), nullable=False),
        sa.Column('original_quantity', sa.Float(), nullable=True),
        sa.Column('purchase_date', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('expiration_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('opened_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('location_id', sa.Integer(), nullable=True),
        sa.Column('price', sa.Float(), nullable=True),
        sa.Column('currency', sa.String(), server_default='USD', nullable=True),
        sa.Column('is_opened', sa.Boolean(), server_default=sa.text('false'), nullable=True),
        sa.Column('is_wasted', sa.Boolean(), server_default=sa.text('false'), nullable=True),
        sa.Column('waste_reason', sa.String(), nullable=True),
        sa.Column('wasted_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('brand', sa.String(), nullable=True),
        sa.Column('store', sa.String(), nullable=True),
        sa.Column('image_url', sa.String(), nullable=True),
        sa.Column('added_by', sa.Integer(), nullable=True),
        sa.Column('receipt_id', sa.Integer(), nullable=True),
        sa.Column('household_id', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['added_by'], ['users.id'], ),
        sa.ForeignKeyConstraint(['household_id'], ['households.id'], ),
        sa.ForeignKeyConstraint(['location_id'], ['storage_locations.id'], ),
        sa.ForeignKeyConstraint(['receipt_id'], ['receipts.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_inventory_items_barcode'), 'inventory_items', ['barcode'], unique=False)
    op.create_index(op.f('ix_inventory_items_name'), 'inventory_items', ['name'], unique=False)

    # Create user_actions table
    op.create_table(
        'user_actions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('action_type', sa.String(), nullable=False),
        sa.Column('entity_type', sa.String(), nullable=False),
        sa.Column('entity_id', sa.Integer(), nullable=False),
        sa.Column('old_state', sa.Text(), nullable=True),
        sa.Column('new_state', sa.Text(), nullable=True),
        sa.Column('is_undone', sa.Boolean(), server_default=sa.text('false'), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create recipes table
    op.create_table(
        'recipes',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('servings', sa.Integer(), server_default='4', nullable=True),
        sa.Column('prep_time_minutes', sa.Integer(), nullable=True),
        sa.Column('cook_time_minutes', sa.Integer(), nullable=True),
        sa.Column('total_time_minutes', sa.Integer(), nullable=True),
        sa.Column('difficulty', sa.String(), nullable=True),
        sa.Column('instructions', sa.Text(), nullable=True),
        sa.Column('cuisine', sa.String(), nullable=True),
        sa.Column('meal_type', sa.String(), nullable=True),
        sa.Column('dietary_tags', sa.JSON(), nullable=True),
        sa.Column('source_url', sa.String(), nullable=True),
        sa.Column('image_url', sa.String(), nullable=True),
        sa.Column('author', sa.String(), nullable=True),
        sa.Column('household_id', sa.Integer(), nullable=True),
        sa.Column('is_favorite', sa.Boolean(), server_default=sa.text('false'), nullable=True),
        sa.Column('times_made', sa.Integer(), server_default='0', nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['household_id'], ['households.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_recipes_name'), 'recipes', ['name'], unique=False)

    # Create ingredients table
    op.create_table(
        'ingredients',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('category', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_ingredients_name'), 'ingredients', ['name'], unique=False)

    # Create recipe_ingredients table
    op.create_table(
        'recipe_ingredients',
        sa.Column('recipe_id', sa.Integer(), nullable=True),
        sa.Column('ingredient_id', sa.Integer(), nullable=True),
        sa.Column('quantity', sa.Float(), nullable=True),
        sa.Column('unit', sa.String(), nullable=True),
        sa.ForeignKeyConstraint(['ingredient_id'], ['ingredients.id'], ),
        sa.ForeignKeyConstraint(['recipe_id'], ['recipes.id'], )
    )

    # Create meal_plans table
    op.create_table(
        'meal_plans',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('household_id', sa.Integer(), nullable=True),
        sa.Column('created_by_id', sa.Integer(), nullable=True),
        sa.Column('recipe_id', sa.Integer(), nullable=True),
        sa.Column('planned_date', sa.DateTime(timezone=True), nullable=False),
        sa.Column('meal_type', sa.String(), nullable=True),
        sa.Column('servings', sa.Integer(), server_default='4', nullable=True),
        sa.Column('is_completed', sa.Boolean(), server_default=sa.text('false'), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['created_by_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['household_id'], ['households.id'], ),
        sa.ForeignKeyConstraint(['recipe_id'], ['recipes.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_meal_plans_planned_date'), 'meal_plans', ['planned_date'], unique=False)

    # Create ai_meal_suggestions table
    op.create_table(
        'ai_meal_suggestions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('household_id', sa.Integer(), nullable=True),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('suggestions', sa.JSON(), nullable=True),
        sa.Column('inventory_snapshot', sa.JSON(), nullable=True),
        sa.Column('ai_provider', sa.String(), nullable=True),
        sa.Column('prompt_tokens', sa.Integer(), nullable=True),
        sa.Column('completion_tokens', sa.Integer(), nullable=True),
        sa.Column('was_accepted', sa.Boolean(), nullable=True),
        sa.Column('accepted_recipe_id', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['accepted_recipe_id'], ['recipes.id'], ),
        sa.ForeignKeyConstraint(['household_id'], ['households.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create shopping_lists table
    op.create_table(
        'shopping_lists',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('household_id', sa.Integer(), nullable=True),
        sa.Column('created_by_id', sa.Integer(), nullable=True),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('store', sa.String(), nullable=True),
        sa.Column('status', sa.Enum('active', 'completed', 'archived', name='shoppingliststatus'), server_default='active', nullable=True),
        sa.Column('generated_from_meal_plan', sa.Boolean(), server_default=sa.text('false'), nullable=True),
        sa.Column('meal_plan_id', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['created_by_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['household_id'], ['households.id'], ),
        sa.ForeignKeyConstraint(['meal_plan_id'], ['meal_plans.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create shopping_list_items table
    op.create_table(
        'shopping_list_items',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('shopping_list_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('quantity', sa.Float(), server_default='1.0', nullable=True),
        sa.Column('unit', sa.String(), nullable=True),
        sa.Column('category', sa.String(), nullable=True),
        sa.Column('aisle', sa.String(), nullable=True),
        sa.Column('estimated_price', sa.Float(), nullable=True),
        sa.Column('actual_price', sa.Float(), nullable=True),
        sa.Column('store', sa.String(), nullable=True),
        sa.Column('is_purchased', sa.Boolean(), server_default=sa.text('false'), nullable=True),
        sa.Column('purchased_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('is_staple', sa.Boolean(), server_default=sa.text('false'), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('already_have_warning', sa.Boolean(), server_default=sa.text('false'), nullable=True),
        sa.Column('inventory_item_id', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['inventory_item_id'], ['inventory_items.id'], ),
        sa.ForeignKeyConstraint(['shopping_list_id'], ['shopping_lists.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create store_aisles table
    op.create_table(
        'store_aisles',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('household_id', sa.Integer(), nullable=True),
        sa.Column('store_name', sa.String(), nullable=False),
        sa.Column('aisle_number', sa.String(), nullable=False),
        sa.Column('aisle_name', sa.String(), nullable=True),
        sa.Column('categories', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['household_id'], ['households.id'], ),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    op.drop_table('store_aisles')
    op.drop_table('shopping_list_items')
    op.drop_table('shopping_lists')
    op.drop_table('ai_meal_suggestions')
    op.drop_index(op.f('ix_meal_plans_planned_date'), table_name='meal_plans')
    op.drop_table('meal_plans')
    op.drop_table('recipe_ingredients')
    op.drop_index(op.f('ix_ingredients_name'), table_name='ingredients')
    op.drop_table('ingredients')
    op.drop_index(op.f('ix_recipes_name'), table_name='recipes')
    op.drop_table('recipes')
    op.drop_table('user_actions')
    op.drop_index(op.f('ix_inventory_items_name'), table_name='inventory_items')
    op.drop_index(op.f('ix_inventory_items_barcode'), table_name='inventory_items')
    op.drop_table('inventory_items')
    op.drop_table('receipt_line_items')
    op.drop_index(op.f('ix_receipts_receipt_number'), table_name='receipts')
    op.drop_table('receipts')
    op.drop_index(op.f('ix_products_name'), table_name='products')
    op.drop_index(op.f('ix_products_barcode'), table_name='products')
    op.drop_table('products')
    op.drop_table('storage_locations')
    op.drop_index(op.f('ix_users_username'), table_name='users')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_table('users')
    op.drop_table('households')
