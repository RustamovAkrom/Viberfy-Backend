import random
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.db import transaction, IntegrityError
from django.utils.text import slugify
from django.utils import timezone
from django.apps import apps
from django.contrib.auth import get_user_model

from faker import Faker

fake = Faker()


class Command(BaseCommand):
    help = "Seed the musics app with fake data (users, artists, albums, tracks, playlists, likes, history)."

    def add_arguments(self, parser):
        parser.add_argument("--artists", type=int, default=20)
        parser.add_argument("--albums", type=int, default=40)
        parser.add_argument("--tracks", type=int, default=100)
        parser.add_argument("--users", type=int, default=20)
        parser.add_argument("--playlists", type=int, default=30)
        parser.add_argument("--likes", type=int, default=100)
        parser.add_argument("--history", type=int, default=200)
        parser.add_argument("--flush", action="store_true")

    def handle(self, *args, **options):
        artists_count = options["artists"]
        albums_count = options["albums"]
        tracks_count = options["tracks"]
        users_count = options["users"]
        playlists_count = options["playlists"]
        likes_count = options["likes"]
        history_count = options["history"]
        do_flush = options["flush"]

        self.stdout.write(self.style.MIGRATE_HEADING("Seeding musics app data..."))

        # Загружаем модели безопасно
        Artist = apps.get_model("musics", "Artist")
        Album = apps.get_model("musics", "Album")
        Track = apps.get_model("musics", "Track")
        Playlist = apps.get_model("musics", "Playlist")

        PlaylistTrack = None
        Like = None
        ListeningHistory = None
        try:
            PlaylistTrack = apps.get_model("musics", "PlaylistTrack")
        except LookupError:
            pass
        try:
            Like = apps.get_model("musics", "Like")
        except LookupError:
            pass
        try:
            ListeningHistory = apps.get_model("musics", "ListeningHistory")
        except LookupError:
            pass

        User = get_user_model()

        # 🔹 Очистка данных
        if do_flush:
            self.stdout.write(self.style.WARNING("Flushing existing musics data..."))
            if ListeningHistory:
                ListeningHistory.objects.all().delete()
            if Like:
                Like.objects.all().delete()
            if PlaylistTrack:
                PlaylistTrack.objects.all().delete()
            Playlist.objects.all().delete()
            Track.objects.all().delete()
            Album.objects.all().delete()
            Artist.objects.all().delete()

        # ------------------------------
        # 1) Users
        # ------------------------------
        created_users = []
        for i in range(users_count):
            username = fake.user_name() + str(random.randint(100, 999))
            email = fake.safe_email()
            u = User(username=username, email=email, is_active=True, is_staff=(i == 0))
            u.set_password("password")
            created_users.append(u)

        User.objects.bulk_create(created_users)
        users_qs = list(User.objects.order_by("-id")[:users_count])
        self.stdout.write(self.style.SUCCESS(f"Created {len(users_qs)} users"))

        # ------------------------------
        # 2) Artists
        # ------------------------------
        artists = [
            Artist(name=fake.unique.company()[:200], bio=fake.text(max_nb_chars=200))
            for _ in range(artists_count)
        ]
        Artist.objects.bulk_create(artists)
        artists_qs = list(Artist.objects.order_by("-id")[:artists_count])
        self.stdout.write(self.style.SUCCESS(f"Created {len(artists_qs)} artists"))

        # ------------------------------
        # 3) Albums
        # ------------------------------
        albums = []
        for _ in range(albums_count):
            artist = random.choice(artists_qs)
            title = fake.sentence(nb_words=3).rstrip(".")[:200]
            slug = slugify(title)[:200]
            release_date = fake.date_between(start_date="-5y", end_date="today")
            albums.append(
                Album(name=title, artist=artist, release_date=release_date, slug=slug)
            )
        Album.objects.bulk_create(albums)
        albums_qs = list(Album.objects.order_by("-id")[:albums_count])
        self.stdout.write(self.style.SUCCESS(f"Created {len(albums_qs)} albums"))

        # ------------------------------
        # 4) Tracks
        # ------------------------------
        genres = ["pop", "rock", "electronic", "hiphop", "jazz", "classical", "indie"]
        tracks = []
        for _ in range(tracks_count):
            artist = random.choice(artists_qs)
            album = (
                random.choice(albums_qs)
                if albums_qs and random.random() > 0.2
                else None
            )
            name = fake.sentence(nb_words=4).rstrip(".")[:200]
            duration = random.randint(60, 420)
            genre = random.choice(genres)
            plays = random.randint(0, 5000)
            likes = random.randint(0, 1000)
            tracks.append(
                Track(
                    name=name,
                    artist=artist,
                    album=album,
                    duration=duration,
                    genre=genre,
                    plays_count=plays,
                    likes_count=likes,
                    is_published=True,
                )
            )
        Track.objects.bulk_create(tracks)
        tracks_qs = list(Track.objects.order_by("-id")[:tracks_count])
        self.stdout.write(self.style.SUCCESS(f"Created {len(tracks_qs)} tracks"))

        # ------------------------------
        # 5) Playlists
        # ------------------------------
        playlists = []
        for _ in range(playlists_count):
            owner = random.choice(users_qs)
            title = fake.sentence(nb_words=3).rstrip(".")[:200]
            playlists.append(
                Playlist(name=title, owner=owner, is_public=random.random() > 0.3)
            )
        Playlist.objects.bulk_create(playlists)
        playlists_qs = list(Playlist.objects.order_by("-id")[:playlists_count])
        self.stdout.write(self.style.SUCCESS(f"Created {len(playlists_qs)} playlists"))

        # PlaylistTrack / ManyToMany
        if PlaylistTrack:
            pt_bulk = []
            for pl in playlists_qs:
                sample_tracks = random.sample(tracks_qs, k=min(10, len(tracks_qs)))
                for order_idx, t in enumerate(sample_tracks, start=1):
                    pt_bulk.append(PlaylistTrack(playlist=pl, track=t, order=order_idx))
            PlaylistTrack.objects.bulk_create(pt_bulk)
            self.stdout.write(
                self.style.SUCCESS(f"Created {len(pt_bulk)} playlist-track relations")
            )
        else:
            for pl in playlists_qs:
                sample_tracks = random.sample(tracks_qs, k=min(10, len(tracks_qs)))
                pl.tracks.add(*sample_tracks)

        # ------------------------------
        # 6) Likes
        # ------------------------------
        if Like:
            like_bulk = []
            seen = set()
            for _ in range(likes_count):
                user = random.choice(users_qs)
                track = random.choice(tracks_qs)
                key = (user.id, track.id)
                if key not in seen:
                    seen.add(key)
                    like_bulk.append(Like(user=user, track=track))
            try:
                Like.objects.bulk_create(like_bulk)
            except IntegrityError:
                for like in like_bulk:
                    try:
                        like.save()
                    except IntegrityError:
                        continue
            self.stdout.write(self.style.SUCCESS(f"Created {len(like_bulk)} likes"))

        # ------------------------------
        # 7) ListeningHistory
        # ------------------------------
        if ListeningHistory:
            hist_bulk = []
            for _ in range(history_count):
                user = random.choice(users_qs)
                track = random.choice(tracks_qs)
                listened_at = timezone.now() - timedelta(
                    days=random.randint(0, 90), minutes=random.randint(0, 1440)
                )
                duration = random.randint(10, getattr(track, "duration", 300))
                hist_bulk.append(
                    ListeningHistory(
                        user=user,
                        track=track,
                        listened_at=listened_at,
                        duration=duration,
                    )
                )
            # bulk_create в маленьких пачках для избежания ошибок транзакции
            batch_size = 50
            for i in range(0, len(hist_bulk), batch_size):
                with transaction.atomic():
                    ListeningHistory.objects.bulk_create(hist_bulk[i : i + batch_size])
            self.stdout.write(
                self.style.SUCCESS(
                    f"Created {len(hist_bulk)} listening history records"
                )
            )

        self.stdout.write(self.style.SUCCESS("Seeding completed."))
        self.stdout.write(
            self.style.WARNING(
                "Default password for created users is 'password' — change it in production!"
            )
        )
