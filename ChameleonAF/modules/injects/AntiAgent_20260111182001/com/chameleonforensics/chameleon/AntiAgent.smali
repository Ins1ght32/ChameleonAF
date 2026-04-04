.class public final Lcom/chameleonforensics/chameleon/AntiAgent;
.super Ljava/lang/Object;
.source "AntiAgent.java"


# annotations
.annotation system Ldalvik/annotation/MemberClasses;
    value = {
        Lcom/chameleonforensics/chameleon/AntiAgent$PkgReceiver;
    }
.end annotation


# static fields
.field private static final TAG:Ljava/lang/String; = "AntiAgent"

.field private static final TARGET_PACKAGE:Ljava/lang/String; = "com.example.helloworld"

.field private static sReceiver:Landroid/content/BroadcastReceiver;

.field private static sRegistered:Z


# direct methods
.method private constructor <init>()V
    .registers 1

    .line 23
    invoke-direct {p0}, Ljava/lang/Object;-><init>()V

    return-void
.end method

.method static synthetic access$000(Landroid/content/Context;Ljava/lang/String;)V
    .registers 2

    .line 14
    invoke-static {p0, p1}, Lcom/chameleonforensics/chameleon/AntiAgent;->recordTriggerCompat(Landroid/content/Context;Ljava/lang/String;)V

    return-void
.end method

.method private static getAppContext()Landroid/content/Context;
    .registers 5

    .line 136
    const/4 v0, 0x0

    :try_start_1
    const-string v1, "android.app.ActivityThread"

    invoke-static {v1}, Ljava/lang/Class;->forName(Ljava/lang/String;)Ljava/lang/Class;

    move-result-object v1

    .line 137
    const-string v2, "currentApplication"

    const/4 v3, 0x0

    new-array v4, v3, [Ljava/lang/Class;

    invoke-virtual {v1, v2, v4}, Ljava/lang/Class;->getMethod(Ljava/lang/String;[Ljava/lang/Class;)Ljava/lang/reflect/Method;

    move-result-object v1

    new-array v2, v3, [Ljava/lang/Object;

    invoke-virtual {v1, v0, v2}, Ljava/lang/reflect/Method;->invoke(Ljava/lang/Object;[Ljava/lang/Object;)Ljava/lang/Object;

    move-result-object v1

    .line 138
    instance-of v2, v1, Landroid/app/Application;

    if-eqz v2, :cond_22

    .line 139
    check-cast v1, Landroid/app/Application;

    invoke-virtual {v1}, Landroid/app/Application;->getApplicationContext()Landroid/content/Context;

    move-result-object v0
    :try_end_20
    .catchall {:try_start_1 .. :try_end_20} :catchall_21

    return-object v0

    .line 141
    :catchall_21
    move-exception v1

    :cond_22
    nop

    .line 142
    return-object v0
.end method

.method private static recordTriggerCompat(Landroid/content/Context;Ljava/lang/String;)V
    .registers 11

    .line 147
    if-nez p0, :cond_6

    invoke-static {}, Lcom/chameleonforensics/chameleon/AntiAgent;->getAppContext()Landroid/content/Context;

    move-result-object p0

    .line 148
    :cond_6
    const-string v0, "AntiAgent"

    if-nez p0, :cond_10

    .line 149
    const-string p0, "recordTriggerCompat: no Context; skipping"

    invoke-static {v0, p0}, Landroid/util/Log;->w(Ljava/lang/String;Ljava/lang/String;)I

    .line 150
    return-void

    .line 153
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

    .line 155
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

    .line 157
    invoke-static {v1}, Ljava/lang/Class;->forName(Ljava/lang/String;)Ljava/lang/Class;

    move-result-object v2

    .line 158
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

    .line 163
    invoke-virtual {p0}, Landroid/content/Context;->getApplicationContext()Landroid/content/Context;

    move-result-object p0

    new-array v3, v4, [Ljava/lang/Object;

    aput-object p0, v3, v7

    aput-object p1, v3, v8

    const/4 p0, 0x0

    invoke-virtual {v2, p0, v3}, Ljava/lang/reflect/Method;->invoke(Ljava/lang/Object;[Ljava/lang/Object;)Ljava/lang/Object;

    .line 164
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

    .line 167
    goto :goto_86

    .line 165
    :catchall_80
    move-exception p0

    .line 166
    const-string p1, "recordTriggerCompat: ReportCore not present/failed; skipping"

    invoke-static {v0, p1, p0}, Landroid/util/Log;->w(Ljava/lang/String;Ljava/lang/String;Ljava/lang/Throwable;)I

    .line 168
    :goto_86
    return-void
.end method

.method private static recordTriggerCompat(Landroid/content/Context;Ljava/lang/String;Ljava/lang/String;)V
    .registers 13

    .line 171
    if-nez p0, :cond_6

    invoke-static {}, Lcom/chameleonforensics/chameleon/AntiAgent;->getAppContext()Landroid/content/Context;

    move-result-object p0

    .line 172
    :cond_6
    const-string v0, "AntiAgent"

    if-nez p0, :cond_10

    .line 173
    const-string p0, "recordTriggerCompat: no Context; skipping"

    invoke-static {v0, p0}, Landroid/util/Log;->w(Ljava/lang/String;Ljava/lang/String;)I

    .line 174
    return-void

    .line 177
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

    .line 179
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

    .line 181
    invoke-static {v1}, Ljava/lang/Class;->forName(Ljava/lang/String;)Ljava/lang/Class;

    move-result-object v2

    .line 182
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

    .line 188
    invoke-virtual {p0}, Landroid/content/Context;->getApplicationContext()Landroid/content/Context;

    move-result-object p0

    new-array v3, v4, [Ljava/lang/Object;

    aput-object p0, v3, v7

    aput-object p1, v3, v8

    aput-object p2, v3, v9

    const/4 p0, 0x0

    invoke-virtual {v2, p0, v3}, Ljava/lang/reflect/Method;->invoke(Ljava/lang/Object;[Ljava/lang/Object;)Ljava/lang/Object;

    .line 189
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

    .line 192
    goto :goto_8d

    .line 190
    :catchall_87
    move-exception p0

    .line 191
    const-string p1, "recordTriggerCompat: ReportCore not present/failed; skipping"

    invoke-static {v0, p1, p0}, Landroid/util/Log;->w(Ljava/lang/String;Ljava/lang/String;Ljava/lang/Throwable;)I

    .line 193
    :goto_8d
    return-void
.end method

.method public static requiresRoot()Z
    .registers 1

    .line 197
    const/4 v0, 0x0

    return v0
.end method

.method public static run()V
    .registers 3

    .line 43
    invoke-static {}, Lcom/chameleonforensics/chameleon/AntiAgent;->getAppContext()Landroid/content/Context;

    move-result-object v0

    .line 44
    const-string v1, "AntiAgent"

    if-nez v0, :cond_e

    .line 45
    const-string v0, "App context unavailable; watcher not started"

    invoke-static {v1, v0}, Landroid/util/Log;->e(Ljava/lang/String;Ljava/lang/String;)I

    .line 46
    return-void

    .line 48
    :cond_e
    const-string v2, "AntiAgent.run() \u2014 starting (no-arg)"

    invoke-static {v1, v2}, Landroid/util/Log;->i(Ljava/lang/String;Ljava/lang/String;)I

    .line 49
    invoke-static {v0}, Lcom/chameleonforensics/chameleon/AntiAgent;->run(Landroid/content/Context;)V

    .line 50
    return-void
.end method

.method public static declared-synchronized run(Landroid/content/Context;)V
    .registers 11

    const-class v0, Lcom/chameleonforensics/chameleon/AntiAgent;

    monitor-enter v0

    .line 54
    :try_start_3
    sget-boolean v1, Lcom/chameleonforensics/chameleon/AntiAgent;->sRegistered:Z

    if-eqz v1, :cond_10

    .line 55
    const-string p0, "AntiAgent"

    const-string v1, "Watcher already registered"

    invoke-static {p0, v1}, Landroid/util/Log;->i(Ljava/lang/String;Ljava/lang/String;)I
    :try_end_e
    .catchall {:try_start_3 .. :try_end_e} :catchall_a0

    .line 56
    monitor-exit v0

    return-void

    .line 59
    :cond_10
    :try_start_10
    new-instance v1, Landroid/content/IntentFilter;

    invoke-direct {v1}, Landroid/content/IntentFilter;-><init>()V

    .line 60
    const-string v2, "android.intent.action.PACKAGE_ADDED"

    invoke-virtual {v1, v2}, Landroid/content/IntentFilter;->addAction(Ljava/lang/String;)V

    .line 61
    const-string v2, "android.intent.action.PACKAGE_REPLACED"

    invoke-virtual {v1, v2}, Landroid/content/IntentFilter;->addAction(Ljava/lang/String;)V

    .line 62
    const-string v2, "package"

    invoke-virtual {v1, v2}, Landroid/content/IntentFilter;->addDataScheme(Ljava/lang/String;)V

    .line 64
    new-instance v2, Lcom/chameleonforensics/chameleon/AntiAgent$PkgReceiver;

    invoke-direct {v2}, Lcom/chameleonforensics/chameleon/AntiAgent$PkgReceiver;-><init>()V

    sput-object v2, Lcom/chameleonforensics/chameleon/AntiAgent;->sReceiver:Landroid/content/BroadcastReceiver;

    .line 66
    sget v2, Landroid/os/Build$VERSION;->SDK_INT:I
    :try_end_2d
    .catchall {:try_start_10 .. :try_end_2d} :catchall_96

    const/16 v3, 0x21

    const/4 v4, 0x1

    if-lt v2, v3, :cond_6a

    .line 69
    :try_start_32
    const-class v2, Landroid/content/Context;

    const-string v3, "registerReceiver"

    const/4 v5, 0x3

    new-array v6, v5, [Ljava/lang/Class;

    const-class v7, Landroid/content/BroadcastReceiver;

    const/4 v8, 0x0

    aput-object v7, v6, v8

    const-class v7, Landroid/content/IntentFilter;

    aput-object v7, v6, v4

    sget-object v7, Ljava/lang/Integer;->TYPE:Ljava/lang/Class;

    const/4 v9, 0x2

    aput-object v7, v6, v9

    .line 70
    invoke-virtual {v2, v3, v6}, Ljava/lang/Class;->getMethod(Ljava/lang/String;[Ljava/lang/Class;)Ljava/lang/reflect/Method;

    move-result-object v2

    .line 74
    invoke-virtual {p0}, Landroid/content/Context;->getApplicationContext()Landroid/content/Context;

    move-result-object p0

    .line 77
    invoke-static {v9}, Ljava/lang/Integer;->valueOf(I)Ljava/lang/Integer;

    move-result-object v3

    new-array v5, v5, [Ljava/lang/Object;

    sget-object v6, Lcom/chameleonforensics/chameleon/AntiAgent;->sReceiver:Landroid/content/BroadcastReceiver;

    aput-object v6, v5, v8

    aput-object v1, v5, v4

    aput-object v3, v5, v9

    .line 74
    invoke-virtual {v2, p0, v5}, Ljava/lang/reflect/Method;->invoke(Ljava/lang/Object;[Ljava/lang/Object;)Ljava/lang/Object;
    :try_end_60
    .catchall {:try_start_32 .. :try_end_60} :catchall_61

    goto :goto_69

    .line 78
    :catchall_61
    move-exception p0

    .line 79
    :try_start_62
    const-string v1, "AntiAgent"

    const-string v2, "Reflection registerReceiver failed"

    invoke-static {v1, v2, p0}, Landroid/util/Log;->e(Ljava/lang/String;Ljava/lang/String;Ljava/lang/Throwable;)I

    .line 80
    :goto_69
    goto :goto_73

    .line 82
    :cond_6a
    invoke-virtual {p0}, Landroid/content/Context;->getApplicationContext()Landroid/content/Context;

    move-result-object p0

    sget-object v2, Lcom/chameleonforensics/chameleon/AntiAgent;->sReceiver:Landroid/content/BroadcastReceiver;

    invoke-virtual {p0, v2, v1}, Landroid/content/Context;->registerReceiver(Landroid/content/BroadcastReceiver;Landroid/content/IntentFilter;)Landroid/content/Intent;

    .line 85
    :goto_73
    sput-boolean v4, Lcom/chameleonforensics/chameleon/AntiAgent;->sRegistered:Z

    .line 86
    const-string p0, "AntiAgent"

    new-instance v1, Ljava/lang/StringBuilder;

    invoke-direct {v1}, Ljava/lang/StringBuilder;-><init>()V

    const-string v2, "Package watcher registered for target=com.example.helloworld (SDK="

    invoke-virtual {v1, v2}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v1

    sget v2, Landroid/os/Build$VERSION;->SDK_INT:I

    invoke-virtual {v1, v2}, Ljava/lang/StringBuilder;->append(I)Ljava/lang/StringBuilder;

    move-result-object v1

    const-string v2, ")"

    invoke-virtual {v1, v2}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v1

    invoke-virtual {v1}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v1

    invoke-static {p0, v1}, Landroid/util/Log;->e(Ljava/lang/String;Ljava/lang/String;)I
    :try_end_95
    .catchall {:try_start_62 .. :try_end_95} :catchall_96

    .line 90
    goto :goto_9e

    .line 88
    :catchall_96
    move-exception p0

    .line 89
    :try_start_97
    const-string v1, "AntiAgent"

    const-string v2, "Failed to register package watcher"

    invoke-static {v1, v2, p0}, Landroid/util/Log;->e(Ljava/lang/String;Ljava/lang/String;Ljava/lang/Throwable;)I
    :try_end_9e
    .catchall {:try_start_97 .. :try_end_9e} :catchall_a0

    .line 91
    :goto_9e
    monitor-exit v0

    return-void

    .line 53
    :catchall_a0
    move-exception p0

    :try_start_a1
    monitor-exit v0
    :try_end_a2
    .catchall {:try_start_a1 .. :try_end_a2} :catchall_a0

    throw p0
.end method

.method public static run(Landroid/app/Activity;)Z
    .registers 3

    .line 32
    const-string v0, "AntiAgent"

    :try_start_2
    const-string v1, "AntiAgent.run() \u2014 starting watcher for: com.example.helloworld"

    invoke-static {v0, v1}, Landroid/util/Log;->i(Ljava/lang/String;Ljava/lang/String;)I

    .line 33
    invoke-virtual {p0}, Landroid/app/Activity;->getApplicationContext()Landroid/content/Context;

    move-result-object p0

    invoke-static {p0}, Lcom/chameleonforensics/chameleon/AntiAgent;->run(Landroid/content/Context;)V
    :try_end_e
    .catch Ljava/lang/Exception; {:try_start_2 .. :try_end_e} :catch_10

    .line 34
    const/4 p0, 0x1

    return p0

    .line 35
    :catch_10
    move-exception p0

    .line 36
    const-string v1, "Error during run"

    invoke-static {v0, v1, p0}, Landroid/util/Log;->e(Ljava/lang/String;Ljava/lang/String;Ljava/lang/Throwable;)I

    .line 37
    const/4 p0, 0x0

    return p0
.end method

.method public static declared-synchronized shutdown(Landroid/content/Context;)V
    .registers 6

    const-class v0, Lcom/chameleonforensics/chameleon/AntiAgent;

    monitor-enter v0

    .line 119
    :try_start_3
    sget-boolean v1, Lcom/chameleonforensics/chameleon/AntiAgent;->sRegistered:Z

    if-eqz v1, :cond_36

    sget-object v1, Lcom/chameleonforensics/chameleon/AntiAgent;->sReceiver:Landroid/content/BroadcastReceiver;
    :try_end_9
    .catchall {:try_start_3 .. :try_end_9} :catchall_38

    if-nez v1, :cond_c

    goto :goto_36

    .line 121
    :cond_c
    const/4 v1, 0x0

    const/4 v2, 0x0

    :try_start_e
    invoke-virtual {p0}, Landroid/content/Context;->getApplicationContext()Landroid/content/Context;

    move-result-object p0

    sget-object v3, Lcom/chameleonforensics/chameleon/AntiAgent;->sReceiver:Landroid/content/BroadcastReceiver;

    invoke-virtual {p0, v3}, Landroid/content/Context;->unregisterReceiver(Landroid/content/BroadcastReceiver;)V

    .line 122
    const-string p0, "AntiAgent"

    const-string v3, "Package watcher unregistered"

    invoke-static {p0, v3}, Landroid/util/Log;->i(Ljava/lang/String;Ljava/lang/String;)I
    :try_end_1e
    .catchall {:try_start_e .. :try_end_1e} :catchall_21

    .line 126
    :try_start_1e
    sput-object v2, Lcom/chameleonforensics/chameleon/AntiAgent;->sReceiver:Landroid/content/BroadcastReceiver;
    :try_end_20
    .catchall {:try_start_1e .. :try_end_20} :catchall_38

    goto :goto_2b

    .line 123
    :catchall_21
    move-exception p0

    .line 124
    :try_start_22
    const-string v3, "AntiAgent"

    const-string v4, "Error unregistering receiver"

    invoke-static {v3, v4, p0}, Landroid/util/Log;->e(Ljava/lang/String;Ljava/lang/String;Ljava/lang/Throwable;)I
    :try_end_29
    .catchall {:try_start_22 .. :try_end_29} :catchall_30

    .line 126
    :try_start_29
    sput-object v2, Lcom/chameleonforensics/chameleon/AntiAgent;->sReceiver:Landroid/content/BroadcastReceiver;

    .line 127
    :goto_2b
    sput-boolean v1, Lcom/chameleonforensics/chameleon/AntiAgent;->sRegistered:Z
    :try_end_2d
    .catchall {:try_start_29 .. :try_end_2d} :catchall_38

    .line 128
    nop

    .line 129
    monitor-exit v0

    return-void

    .line 126
    :catchall_30
    move-exception p0

    :try_start_31
    sput-object v2, Lcom/chameleonforensics/chameleon/AntiAgent;->sReceiver:Landroid/content/BroadcastReceiver;

    .line 127
    sput-boolean v1, Lcom/chameleonforensics/chameleon/AntiAgent;->sRegistered:Z

    .line 128
    throw p0
    :try_end_36
    .catchall {:try_start_31 .. :try_end_36} :catchall_38

    .line 119
    :cond_36
    :goto_36
    monitor-exit v0

    return-void

    .line 118
    :catchall_38
    move-exception p0

    :try_start_39
    monitor-exit v0
    :try_end_3a
    .catchall {:try_start_39 .. :try_end_3a} :catchall_38

    throw p0
.end method
