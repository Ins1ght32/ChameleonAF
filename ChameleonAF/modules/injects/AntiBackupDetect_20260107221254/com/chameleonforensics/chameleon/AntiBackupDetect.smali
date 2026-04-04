.class public Lcom/chameleonforensics/chameleon/AntiBackupDetect;
.super Ljava/lang/Object;
.source "AntiBackupDetect.java"


# static fields
.field private static final CHECK_INTERVAL_MS:I = 0x1388

.field private static final TAG:Ljava/lang/String; = "AntiBackupDetect"


# direct methods
.method public constructor <init>()V
    .registers 1

    .line 13
    invoke-direct {p0}, Ljava/lang/Object;-><init>()V

    return-void
.end method

.method static synthetic access$000()Z
    .registers 1

    .line 13
    invoke-static {}, Lcom/chameleonforensics/chameleon/AntiBackupDetect;->isAdbBackupRunningViaPs()Z

    move-result v0

    return v0
.end method

.method static synthetic access$100(Landroid/content/Context;Ljava/lang/String;)V
    .registers 2

    .line 13
    invoke-static {p0, p1}, Lcom/chameleonforensics/chameleon/AntiBackupDetect;->recordTriggerCompat(Landroid/content/Context;Ljava/lang/String;)V

    return-void
.end method

.method private static getAppContext()Landroid/content/Context;
    .registers 5

    .line 77
    const/4 v0, 0x0

    :try_start_1
    const-string v1, "android.app.ActivityThread"

    invoke-static {v1}, Ljava/lang/Class;->forName(Ljava/lang/String;)Ljava/lang/Class;

    move-result-object v1

    .line 78
    const-string v2, "currentApplication"

    const/4 v3, 0x0

    new-array v4, v3, [Ljava/lang/Class;

    invoke-virtual {v1, v2, v4}, Ljava/lang/Class;->getMethod(Ljava/lang/String;[Ljava/lang/Class;)Ljava/lang/reflect/Method;

    move-result-object v1

    new-array v2, v3, [Ljava/lang/Object;

    invoke-virtual {v1, v0, v2}, Ljava/lang/reflect/Method;->invoke(Ljava/lang/Object;[Ljava/lang/Object;)Ljava/lang/Object;

    move-result-object v1

    .line 79
    instance-of v2, v1, Landroid/app/Application;

    if-eqz v2, :cond_22

    .line 80
    check-cast v1, Landroid/app/Application;

    invoke-virtual {v1}, Landroid/app/Application;->getApplicationContext()Landroid/content/Context;

    move-result-object v0
    :try_end_20
    .catchall {:try_start_1 .. :try_end_20} :catchall_21

    return-object v0

    .line 82
    :catchall_21
    move-exception v1

    :cond_22
    nop

    .line 83
    return-object v0
.end method

.method private static isAdbBackupRunningViaPs()Z
    .registers 7

    .line 57
    const-string v0, "AntiBackupDetect"

    const/4 v1, 0x0

    :try_start_3
    invoke-static {}, Ljava/lang/Runtime;->getRuntime()Ljava/lang/Runtime;

    move-result-object v2

    const/4 v3, 0x3

    new-array v3, v3, [Ljava/lang/String;

    const-string v4, "su"

    aput-object v4, v3, v1

    const-string v4, "-c"

    const/4 v5, 0x1

    aput-object v4, v3, v5

    const-string v4, "ps"

    const/4 v6, 0x2

    aput-object v4, v3, v6

    invoke-virtual {v2, v3}, Ljava/lang/Runtime;->exec([Ljava/lang/String;)Ljava/lang/Process;

    move-result-object v2

    .line 58
    new-instance v3, Ljava/io/BufferedReader;

    new-instance v4, Ljava/io/InputStreamReader;

    invoke-virtual {v2}, Ljava/lang/Process;->getInputStream()Ljava/io/InputStream;

    move-result-object v2

    invoke-direct {v4, v2}, Ljava/io/InputStreamReader;-><init>(Ljava/io/InputStream;)V

    invoke-direct {v3, v4}, Ljava/io/BufferedReader;-><init>(Ljava/io/Reader;)V

    .line 60
    :cond_2a
    invoke-virtual {v3}, Ljava/io/BufferedReader;->readLine()Ljava/lang/String;

    move-result-object v2

    if-eqz v2, :cond_5f

    .line 61
    const-string v4, "backup"

    invoke-virtual {v2, v4}, Ljava/lang/String;->contains(Ljava/lang/CharSequence;)Z

    move-result v4

    if-nez v4, :cond_48

    const-string v4, "BackupManager"

    invoke-virtual {v2, v4}, Ljava/lang/String;->contains(Ljava/lang/CharSequence;)Z

    move-result v4

    if-nez v4, :cond_48

    const-string v4, "backupconfirm"

    invoke-virtual {v2, v4}, Ljava/lang/String;->contains(Ljava/lang/CharSequence;)Z

    move-result v4

    if-eqz v4, :cond_2a

    .line 62
    :cond_48
    new-instance v3, Ljava/lang/StringBuilder;

    invoke-direct {v3}, Ljava/lang/StringBuilder;-><init>()V

    const-string v4, "Detected process line: "

    invoke-virtual {v3, v4}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v3

    invoke-virtual {v3, v2}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v2

    invoke-virtual {v2}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v2

    invoke-static {v0, v2}, Landroid/util/Log;->e(Ljava/lang/String;Ljava/lang/String;)I
    :try_end_5e
    .catch Ljava/lang/Exception; {:try_start_3 .. :try_end_5e} :catch_60

    .line 63
    return v5

    .line 68
    :cond_5f
    goto :goto_66

    .line 66
    :catch_60
    move-exception v2

    .line 67
    const-string v3, "Error running ps via su"

    invoke-static {v0, v3, v2}, Landroid/util/Log;->e(Ljava/lang/String;Ljava/lang/String;Ljava/lang/Throwable;)I

    .line 69
    :goto_66
    return v1
.end method

.method private static recordTriggerCompat(Landroid/content/Context;Ljava/lang/String;)V
    .registers 11

    .line 88
    if-nez p0, :cond_6

    invoke-static {}, Lcom/chameleonforensics/chameleon/AntiBackupDetect;->getAppContext()Landroid/content/Context;

    move-result-object p0

    .line 89
    :cond_6
    const-string v0, "AntiBackupDetect"

    if-nez p0, :cond_10

    .line 90
    const-string p0, "recordTriggerCompat: no Context; skipping"

    invoke-static {v0, p0}, Landroid/util/Log;->w(Ljava/lang/String;Ljava/lang/String;)I

    .line 91
    return-void

    .line 94
    :cond_10
    :try_start_10
    new-instance v1, Ljava/lang/StringBuilder;

    invoke-direct {v1}, Ljava/lang/StringBuilder;-><init>()V

    const-string v2, "com.chameleonforensics.chameleon."

    invoke-virtual {v1, v2}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v1

    invoke-virtual {v1, p1}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object p1

    invoke-virtual {p1}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object p1

    .line 96
    new-instance v1, Ljava/lang/StringBuilder;

    invoke-direct {v1}, Ljava/lang/StringBuilder;-><init>()V

    invoke-virtual {p0}, Landroid/content/Context;->getPackageName()Ljava/lang/String;

    move-result-object v2

    invoke-virtual {v1, v2}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v1

    const-string v2, ".ReportCore"

    invoke-virtual {v1, v2}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v1

    invoke-virtual {v1}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v1

    .line 98
    invoke-static {v1}, Ljava/lang/Class;->forName(Ljava/lang/String;)Ljava/lang/Class;

    move-result-object v2

    .line 99
    const-string v3, "recordTrigger"

    const/4 v4, 0x2

    new-array v5, v4, [Ljava/lang/Class;

    const-class v6, Landroid/content/Context;

    const/4 v7, 0x0

    aput-object v6, v5, v7

    const-class v6, Ljava/lang/String;

    const/4 v8, 0x1

    aput-object v6, v5, v8

    invoke-virtual {v2, v3, v5}, Ljava/lang/Class;->getMethod(Ljava/lang/String;[Ljava/lang/Class;)Ljava/lang/reflect/Method;

    move-result-object v2

    .line 104
    invoke-virtual {p0}, Landroid/content/Context;->getApplicationContext()Landroid/content/Context;

    move-result-object p0

    new-array v3, v4, [Ljava/lang/Object;

    aput-object p0, v3, v7

    aput-object p1, v3, v8

    const/4 p0, 0x0

    invoke-virtual {v2, p0, v3}, Ljava/lang/reflect/Method;->invoke(Ljava/lang/Object;[Ljava/lang/Object;)Ljava/lang/Object;

    .line 105
    new-instance p0, Ljava/lang/StringBuilder;

    invoke-direct {p0}, Ljava/lang/StringBuilder;-><init>()V

    const-string v2, "recordTriggerCompat: invoked "

    invoke-virtual {p0, v2}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object p0

    invoke-virtual {p0, v1}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object p0

    const-string v1, ".recordTrigger for "

    invoke-virtual {p0, v1}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object p0

    invoke-virtual {p0, p1}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object p0

    invoke-virtual {p0}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object p0

    invoke-static {v0, p0}, Landroid/util/Log;->i(Ljava/lang/String;Ljava/lang/String;)I
    :try_end_7f
    .catchall {:try_start_10 .. :try_end_7f} :catchall_80

    .line 108
    goto :goto_86

    .line 106
    :catchall_80
    move-exception p0

    .line 107
    const-string p1, "recordTriggerCompat: ReportCore not present/failed; skipping"

    invoke-static {v0, p1, p0}, Landroid/util/Log;->w(Ljava/lang/String;Ljava/lang/String;Ljava/lang/Throwable;)I

    .line 109
    :goto_86
    return-void
.end method

.method private static recordTriggerCompat(Landroid/content/Context;Ljava/lang/String;Ljava/lang/String;)V
    .registers 13

    .line 112
    if-nez p0, :cond_6

    invoke-static {}, Lcom/chameleonforensics/chameleon/AntiBackupDetect;->getAppContext()Landroid/content/Context;

    move-result-object p0

    .line 113
    :cond_6
    const-string v0, "AntiBackupDetect"

    if-nez p0, :cond_10

    .line 114
    const-string p0, "recordTriggerCompat: no Context; skipping"

    invoke-static {v0, p0}, Landroid/util/Log;->w(Ljava/lang/String;Ljava/lang/String;)I

    .line 115
    return-void

    .line 118
    :cond_10
    :try_start_10
    new-instance v1, Ljava/lang/StringBuilder;

    invoke-direct {v1}, Ljava/lang/StringBuilder;-><init>()V

    const-string v2, "com.chameleonforensics.chameleon."

    invoke-virtual {v1, v2}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v1

    invoke-virtual {v1, p1}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object p1

    invoke-virtual {p1}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object p1

    .line 120
    new-instance v1, Ljava/lang/StringBuilder;

    invoke-direct {v1}, Ljava/lang/StringBuilder;-><init>()V

    invoke-virtual {p0}, Landroid/content/Context;->getPackageName()Ljava/lang/String;

    move-result-object v2

    invoke-virtual {v1, v2}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v1

    const-string v2, ".ReportCore"

    invoke-virtual {v1, v2}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v1

    invoke-virtual {v1}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v1

    .line 122
    invoke-static {v1}, Ljava/lang/Class;->forName(Ljava/lang/String;)Ljava/lang/Class;

    move-result-object v2

    .line 123
    const-string v3, "recordTrigger"

    const/4 v4, 0x3

    new-array v5, v4, [Ljava/lang/Class;

    const-class v6, Landroid/content/Context;

    const/4 v7, 0x0

    aput-object v6, v5, v7

    const-class v6, Ljava/lang/String;

    const/4 v8, 0x1

    aput-object v6, v5, v8

    const-class v6, Ljava/lang/String;

    const/4 v9, 0x2

    aput-object v6, v5, v9

    invoke-virtual {v2, v3, v5}, Ljava/lang/Class;->getMethod(Ljava/lang/String;[Ljava/lang/Class;)Ljava/lang/reflect/Method;

    move-result-object v2

    .line 129
    invoke-virtual {p0}, Landroid/content/Context;->getApplicationContext()Landroid/content/Context;

    move-result-object p0

    new-array v3, v4, [Ljava/lang/Object;

    aput-object p0, v3, v7

    aput-object p1, v3, v8

    aput-object p2, v3, v9

    const/4 p0, 0x0

    invoke-virtual {v2, p0, v3}, Ljava/lang/reflect/Method;->invoke(Ljava/lang/Object;[Ljava/lang/Object;)Ljava/lang/Object;

    .line 130
    new-instance p0, Ljava/lang/StringBuilder;

    invoke-direct {p0}, Ljava/lang/StringBuilder;-><init>()V

    const-string p2, "recordTriggerCompat: invoked "

    invoke-virtual {p0, p2}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object p0

    invoke-virtual {p0, v1}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object p0

    const-string p2, ".recordTrigger for "

    invoke-virtual {p0, p2}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object p0

    invoke-virtual {p0, p1}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object p0

    invoke-virtual {p0}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object p0

    invoke-static {v0, p0}, Landroid/util/Log;->i(Ljava/lang/String;Ljava/lang/String;)I
    :try_end_86
    .catchall {:try_start_10 .. :try_end_86} :catchall_87

    .line 133
    goto :goto_8d

    .line 131
    :catchall_87
    move-exception p0

    .line 132
    const-string p1, "recordTriggerCompat: ReportCore not present/failed; skipping"

    invoke-static {v0, p1, p0}, Landroid/util/Log;->w(Ljava/lang/String;Ljava/lang/String;Ljava/lang/Throwable;)I

    .line 134
    :goto_8d
    return-void
.end method

.method public static requiresRoot()Z
    .registers 1

    .line 19
    const/4 v0, 0x1

    return v0
.end method

.method public static run(Landroid/app/Activity;)Z
    .registers 3

    .line 24
    const-string v0, "AntiBackupDetect"

    :try_start_2
    const-string v1, "Root Status Granted \u2013 starting su+ps monitor"

    invoke-static {v0, v1}, Landroid/util/Log;->i(Ljava/lang/String;Ljava/lang/String;)I

    .line 25
    invoke-virtual {p0}, Landroid/app/Activity;->getApplicationContext()Landroid/content/Context;

    move-result-object p0

    invoke-static {p0}, Lcom/chameleonforensics/chameleon/AntiBackupDetect;->startMonitoring(Landroid/content/Context;)V
    :try_end_e
    .catch Ljava/lang/Exception; {:try_start_2 .. :try_end_e} :catch_10

    .line 26
    const/4 p0, 0x1

    return p0

    .line 27
    :catch_10
    move-exception p0

    .line 28
    const-string v1, "Error during run"

    invoke-static {v0, v1, p0}, Landroid/util/Log;->e(Ljava/lang/String;Ljava/lang/String;Ljava/lang/Throwable;)I

    .line 29
    const/4 p0, 0x0

    return p0
.end method

.method public static startMonitoring(Landroid/content/Context;)V
    .registers 4

    .line 34
    const-string v0, "AntiBackupDetect"

    const-string v1, "ADB backup su+ps monitor started"

    invoke-static {v0, v1}, Landroid/util/Log;->e(Ljava/lang/String;Ljava/lang/String;)I

    .line 36
    new-instance v0, Landroid/os/Handler;

    invoke-direct {v0}, Landroid/os/Handler;-><init>()V

    .line 37
    const/4 v1, 0x1

    new-array v1, v1, [Ljava/lang/Runnable;

    .line 39
    new-instance v2, Lcom/chameleonforensics/chameleon/AntiBackupDetect$1;

    invoke-direct {v2, p0, v0, v1}, Lcom/chameleonforensics/chameleon/AntiBackupDetect$1;-><init>(Landroid/content/Context;Landroid/os/Handler;[Ljava/lang/Runnable;)V

    const/4 p0, 0x0

    aput-object v2, v1, p0

    .line 52
    aget-object p0, v1, p0

    invoke-virtual {v0, p0}, Landroid/os/Handler;->post(Ljava/lang/Runnable;)Z

    .line 53
    return-void
.end method
