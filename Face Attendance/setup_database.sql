-- Enable UUID extension
create extension if not exists "uuid-ossp";

-- Create users table
create table if not exists users (
    id uuid references auth.users primary key,
    username text unique not null,
    email text unique not null,
    role text not null check (role in ('admin', 'student')),
    created_at timestamp with time zone default timezone('utc'::text, now()) not null
);

-- Create attendance table
create table if not exists attendance (
    id uuid default uuid_generate_v4() primary key,
    student_id uuid references users(id) not null,
    status text not null check (status in ('present', 'absent')),
    timestamp timestamp with time zone default timezone('utc'::text, now()) not null
);

-- Create RLS policies
alter table users enable row level security;
alter table attendance enable row level security;

-- Allow service role to bypass RLS
alter table users force row level security;
alter table attendance force row level security;

-- Policy for users table
create policy "Enable read access for all users"
    on users for select
    using (true);

create policy "Enable insert for service role"
    on users for insert
    with check (true);

create policy "Enable update for users based on role"
    on users for update using (
        auth.uid() = id or 
        exists (
            select 1 from users
            where users.id = auth.uid()
            and users.role = 'admin'
        )
    );

-- Policy for attendance table
create policy "Enable read access for own records and admins"
    on attendance for select using (
        student_id = auth.uid() or
        exists (
            select 1 from users
            where users.id = auth.uid()
            and users.role = 'admin'
        )
    );

create policy "Enable insert for own records"
    on attendance for insert
    with check (student_id = auth.uid());

create policy "Enable all access for admins"
    on attendance for all using (
        exists (
            select 1 from users
            where users.id = auth.uid()
            and users.role = 'admin'
        )
    ); 