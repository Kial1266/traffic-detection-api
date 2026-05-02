-- Supabase (PostgreSQL) schema for traffic logs

create table if not exists public.traffic_logs (
    id bigserial primary key,
    waktu_frame integer not null check (waktu_frame >= 0),
    jumlah_kendaraan integer not null check (jumlah_kendaraan >= 0),
    status text not null,
    created_at timestamptz not null default now()
);

create index if not exists traffic_logs_timestamp_idx
    on public.traffic_logs (created_at desc);

create index if not exists traffic_logs_status_idx
    on public.traffic_logs (status);
