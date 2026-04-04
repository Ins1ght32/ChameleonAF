.class public Lcom/chameleonforensics/chameleon/ADBScreenCapture;
.super Ljava/lang/Object;
.source "ADBScreenCapture.java"


# static fields
.field private static final TAG:Ljava/lang/String; = "ADBScreenCapture"

.field private static monitorThread:Ljava/lang/Thread;

.field private static volatile running:Z


# direct methods
.method static constructor <clinit>()V
    .registers 1

    .line 26
    const/4 v0, 0x1

    sput-boolean v0, Lcom/chameleonforensics/chameleon/ADBScreenCapture;->running:Z

    return-void
.end method

.method public constructor <init>()V
    .registers 1

    .line 21
    invoke-direct {p0}, Ljava/lang/Object;-><init>()V

    return-void
.end method

.method private static getAppContext()Landroid/content/Context;
    .registers 5

    .line 89
    const/4 v0, 0x0

    :try_start_1
    const-string v1, "android.app.ActivityThread"

    invoke-static {v1}, Ljava/lang/Class;->forName(Ljava/lang/String;)Ljava/lang/Class;

    move-result-object v1

    .line 90
    const-string v2, "currentApplication"

    const/4 v3, 0x0

    new-array v4, v3, [Ljava/lang/Class;

    invoke-virtual {v1, v2, v4}, Ljava/lang/Class;->getMethod(Ljava/lang/String;[Ljava/lang/Class;)Ljava/lang/reflect/Method;

    move-result-object v1

    new-array v2, v3, [Ljava/lang/Object;

    invoke-virtual {v1, v0, v2}, Ljava/lang/reflect/Method;->invoke(Ljava/lang/Object;[Ljava/lang/Object;)Ljava/lang/Object;

    move-result-object v1

    .line 91
    instance-of v2, v1, Landroid/app/Application;

    if-eqz v2, :cond_22

    .line 92
    check-cast v1, Landroid/app/Application;

    invoke-virtual {v1}, Landroid/app/Application;->getApplicationContext()Landroid/content/Context;

    move-result-object v0
    :try_end_20
    .catchall {:try_start_1 .. :try_end_20} :catchall_21

    return-object v0

    .line 94
    :catchall_21
    move-exception v1

    :cond_22
    nop

    .line 95
    return-object v0
.end method

.method static synthetic lambda$startMonitoring$0(Landroid/content/Context;)V
    .registers 9

    .line 40
    const-string v0, "ADBScreenCapture"

    const-string v1, ""

    .line 41
    :goto_4
    sget-boolean v2, Lcom/chameleonforensics/chameleon/ADBScreenCapture;->running:Z

    if-eqz v2, :cond_82

    .line 44
    :try_start_8
    const-string v2, "ps -A | grep -w screencap"

    invoke-static {v2}, Lcom/chameleonforensics/chameleon/ADBScreenCapture;->runSuCommand(Ljava/lang/String;)Ljava/lang/Process;

    move-result-object v2

    .line 46
    new-instance v3, Ljava/io/BufferedReader;

    new-instance v4, Ljava/io/InputStreamReader;

    .line 47
    invoke-virtual {v2}, Ljava/lang/Process;->getInputStream()Ljava/io/InputStream;

    move-result-object v5

    invoke-direct {v4, v5}, Ljava/io/InputStreamReader;-><init>(Ljava/io/InputStream;)V

    invoke-direct {v3, v4}, Ljava/io/BufferedReader;-><init>(Ljava/io/Reader;)V

    .line 50
    :cond_1c
    :goto_1c
    invoke-virtual {v3}, Ljava/io/BufferedReader;->readLine()Ljava/lang/String;

    move-result-object v4

    if-eqz v4, :cond_6f

    .line 51
    invoke-virtual {v4}, Ljava/lang/String;->trim()Ljava/lang/String;

    move-result-object v4

    .line 52
    invoke-virtual {v4}, Ljava/lang/String;->isEmpty()Z

    move-result v5

    if-nez v5, :cond_1c

    .line 53
    const-string v5, "\\s+"

    invoke-virtual {v4, v5}, Ljava/lang/String;->split(Ljava/lang/String;)[Ljava/lang/String;

    move-result-object v4

    .line 54
    array-length v5, v4

    const/4 v6, 0x2

    if-le v5, v6, :cond_6e

    .line 55
    const/4 v5, 0x0

    aget-object v5, v4, v5

    .line 56
    const/4 v6, 0x1

    aget-object v4, v4, v6

    .line 58
    const-string v6, "shell"

    invoke-virtual {v6, v5}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z

    move-result v6

    if-eqz v6, :cond_6e

    invoke-virtual {v4, v1}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z

    move-result v6

    if-nez v6, :cond_6e

    .line 59
    new-instance v6, Ljava/lang/StringBuilder;

    invoke-direct {v6}, Ljava/lang/StringBuilder;-><init>()V

    const-string v7, "ADB screencap detected! PID="

    invoke-virtual {v6, v7}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v6

    invoke-virtual {v6, v4}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v6

    const-string v7, " User="

    invoke-virtual {v6, v7}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v6

    invoke-virtual {v6, v5}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v5

    invoke-virtual {v5}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v5

    invoke-static {v0, v5}, Landroid/util/Log;->e(Ljava/lang/String;Ljava/lang/String;)I

    .line 60
    invoke-static {p0, v0}, Lcom/chameleonforensics/chameleon/ADBScreenCapture;->recordTriggerCompat(Landroid/content/Context;Ljava/lang/String;)V

    .line 61
    move-object v1, v4

    .line 64
    :cond_6e
    goto :goto_1c

    .line 66
    :cond_6f
    invoke-virtual {v3}, Ljava/io/BufferedReader;->close()V

    .line 67
    invoke-virtual {v2}, Ljava/lang/Process;->waitFor()I

    .line 68
    const-wide/16 v2, 0xc8

    invoke-static {v2, v3}, Ljava/lang/Thread;->sleep(J)V
    :try_end_7a
    .catch Ljava/lang/Exception; {:try_start_8 .. :try_end_7a} :catch_7b

    goto :goto_81

    .line 69
    :catch_7b
    move-exception v2

    .line 70
    const-string v3, "Error in monitor loop"

    invoke-static {v0, v3, v2}, Landroid/util/Log;->e(Ljava/lang/String;Ljava/lang/String;Ljava/lang/Throwable;)I

    .line 71
    :goto_81
    goto :goto_4

    .line 73
    :cond_82
    return-void
.end method

.method private static recordTriggerCompat(Landroid/content/Context;Ljava/lang/String;)V
    .registers 11

    .line 99
    if-nez p0, :cond_6

    invoke-static {}, Lcom/chameleonforensics/chameleon/ADBScreenCapture;->getAppContext()Landroid/content/Context;

    move-result-object p0

    .line 100
    :cond_6
    const-string v0, "ADBScreenCapture"

    if-nez p0, :cond_10

    .line 101
    const-string p0, "recordTriggerCompat: no Context; skipping"

    invoke-static {v0, p0}, Landroid/util/Log;->w(Ljava/lang/String;Ljava/lang/String;)I

    .line 102
    return-void

    .line 105
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

    .line 107
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

    .line 109
    invoke-static {v1}, Ljava/lang/Class;->forName(Ljava/lang/String;)Ljava/lang/Class;

    move-result-object v2

    .line 110
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

    .line 115
    invoke-virtual {p0}, Landroid/content/Context;->getApplicationContext()Landroid/content/Context;

    move-result-object p0

    new-array v3, v4, [Ljava/lang/Object;

    aput-object p0, v3, v7

    aput-object p1, v3, v8

    const/4 p0, 0x0

    invoke-virtual {v2, p0, v3}, Ljava/lang/reflect/Method;->invoke(Ljava/lang/Object;[Ljava/lang/Object;)Ljava/lang/Object;

    .line 116
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

    .line 119
    goto :goto_86

    .line 117
    :catchall_80
    move-exception p0

    .line 118
    const-string p1, "recordTriggerCompat: ReportCore not present/failed; skipping"

    invoke-static {v0, p1, p0}, Landroid/util/Log;->w(Ljava/lang/String;Ljava/lang/String;Ljava/lang/Throwable;)I

    .line 120
    :goto_86
    return-void
.end method

.method private static recordTriggerCompat(Landroid/content/Context;Ljava/lang/String;Ljava/lang/String;)V
    .registers 13

    .line 123
    if-nez p0, :cond_6

    invoke-static {}, Lcom/chameleonforensics/chameleon/ADBScreenCapture;->getAppContext()Landroid/content/Context;

    move-result-object p0

    .line 124
    :cond_6
    const-string v0, "ADBScreenCapture"

    if-nez p0, :cond_10

    .line 125
    const-string p0, "recordTriggerCompat: no Context; skipping"

    invoke-static {v0, p0}, Landroid/util/Log;->w(Ljava/lang/String;Ljava/lang/String;)I

    .line 126
    return-void

    .line 129
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

    .line 131
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

    .line 133
    invoke-static {v1}, Ljava/lang/Class;->forName(Ljava/lang/String;)Ljava/lang/Class;

    move-result-object v2

    .line 134
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

    .line 140
    invoke-virtual {p0}, Landroid/content/Context;->getApplicationContext()Landroid/content/Context;

    move-result-object p0

    new-array v3, v4, [Ljava/lang/Object;

    aput-object p0, v3, v7

    aput-object p1, v3, v8

    aput-object p2, v3, v9

    const/4 p0, 0x0

    invoke-virtual {v2, p0, v3}, Ljava/lang/reflect/Method;->invoke(Ljava/lang/Object;[Ljava/lang/Object;)Ljava/lang/Object;

    .line 141
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

    .line 144
    goto :goto_8d

    .line 142
    :catchall_87
    move-exception p0

    .line 143
    const-string p1, "recordTriggerCompat: ReportCore not present/failed; skipping"

    invoke-static {v0, p1, p0}, Landroid/util/Log;->w(Ljava/lang/String;Ljava/lang/String;Ljava/lang/Throwable;)I

    .line 145
    :goto_8d
    return-void
.end method

.method public static requiresRoot()Z
    .registers 1

    .line 150
    const/4 v0, 0x1

    return v0
.end method

.method public static run(Landroid/app/Activity;)Z
    .registers 3

    .line 33
    const-string v0, "ADBScreenCapture"

    const-string v1, "Root Status Granted \u2013 starting ADB Screen Capture Monitoring"

    invoke-static {v0, v1}, Landroid/util/Log;->i(Ljava/lang/String;Ljava/lang/String;)I

    .line 34
    if-eqz p0, :cond_e

    invoke-virtual {p0}, Landroid/app/Activity;->getApplicationContext()Landroid/content/Context;

    move-result-object p0

    goto :goto_12

    :cond_e
    invoke-static {}, Lcom/chameleonforensics/chameleon/ADBScreenCapture;->getAppContext()Landroid/content/Context;

    move-result-object p0

    :goto_12
    invoke-static {p0}, Lcom/chameleonforensics/chameleon/ADBScreenCapture;->startMonitoring(Landroid/content/Context;)V

    .line 35
    const/4 p0, 0x1

    return p0
.end method

.method private static runSuCommand(Ljava/lang/String;)Ljava/lang/Process;
    .registers 5
    .annotation system Ldalvik/annotation/Throws;
        value = {
            Ljava/lang/Exception;
        }
    .end annotation

    .line 81
    invoke-static {}, Ljava/lang/Runtime;->getRuntime()Ljava/lang/Runtime;

    move-result-object v0

    const/4 v1, 0x3

    new-array v1, v1, [Ljava/lang/String;

    const/4 v2, 0x0

    const-string v3, "su"

    aput-object v3, v1, v2

    const/4 v2, 0x1

    const-string v3, "-c"

    aput-object v3, v1, v2

    const/4 v2, 0x2

    aput-object p0, v1, v2

    invoke-virtual {v0, v1}, Ljava/lang/Runtime;->exec([Ljava/lang/String;)Ljava/lang/Process;

    move-result-object p0

    return-object p0
.end method

.method private static startMonitoring(Landroid/content/Context;)V
    .registers 3

    .line 39
    new-instance v0, Ljava/lang/Thread;

    new-instance v1, Lcom/chameleonforensics/chameleon/ADBScreenCapture$$ExternalSyntheticLambda0;

    invoke-direct {v1, p0}, Lcom/chameleonforensics/chameleon/ADBScreenCapture$$ExternalSyntheticLambda0;-><init>(Landroid/content/Context;)V

    invoke-direct {v0, v1}, Ljava/lang/Thread;-><init>(Ljava/lang/Runnable;)V

    sput-object v0, Lcom/chameleonforensics/chameleon/ADBScreenCapture;->monitorThread:Ljava/lang/Thread;

    .line 74
    sget-object p0, Lcom/chameleonforensics/chameleon/ADBScreenCapture;->monitorThread:Ljava/lang/Thread;

    invoke-virtual {p0}, Ljava/lang/Thread;->start()V

    .line 75
    return-void
.end method
