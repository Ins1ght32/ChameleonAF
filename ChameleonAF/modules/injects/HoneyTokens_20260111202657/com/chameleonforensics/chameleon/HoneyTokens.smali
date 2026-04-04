.class public Lcom/chameleonforensics/chameleon/HoneyTokens;
.super Ljava/lang/Object;
.source "HoneyTokens.java"


# static fields
.field private static final TAG:Ljava/lang/String; = "HoneyTokens"

.field private static final deployedFiles:Ljava/util/List;
    .annotation system Ldalvik/annotation/Signature;
        value = {
            "Ljava/util/List<",
            "Ljava/lang/String;",
            ">;"
        }
    .end annotation
.end field

.field private static volatile monitoringActive:Z


# direct methods
.method static constructor <clinit>()V
    .registers 1

    .line 25
    new-instance v0, Ljava/util/ArrayList;

    invoke-direct {v0}, Ljava/util/ArrayList;-><init>()V

    sput-object v0, Lcom/chameleonforensics/chameleon/HoneyTokens;->deployedFiles:Ljava/util/List;

    .line 26
    const/4 v0, 0x0

    sput-boolean v0, Lcom/chameleonforensics/chameleon/HoneyTokens;->monitoringActive:Z

    return-void
.end method

.method public constructor <init>()V
    .registers 1

    .line 21
    invoke-direct {p0}, Ljava/lang/Object;-><init>()V

    return-void
.end method

.method private static deployHoneytokens(Landroid/content/Context;)V
    .registers 7

    .line 64
    :try_start_0
    new-instance p0, Ljava/text/SimpleDateFormat;

    const-string v0, "yyyyMMdd_HHmmss"

    invoke-direct {p0, v0}, Ljava/text/SimpleDateFormat;-><init>(Ljava/lang/String;)V

    new-instance v0, Ljava/util/Date;

    invoke-direct {v0}, Ljava/util/Date;-><init>()V

    invoke-virtual {p0, v0}, Ljava/text/SimpleDateFormat;->format(Ljava/util/Date;)Ljava/lang/String;

    move-result-object p0

    .line 65
    new-instance v0, Ljava/lang/StringBuilder;

    invoke-direct {v0}, Ljava/lang/StringBuilder;-><init>()V

    const-string v1, "honeytoken_"

    invoke-virtual {v0, v1}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v0

    invoke-virtual {v0, p0}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v0

    const-string v1, ".txt"

    invoke-virtual {v0, v1}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v0

    invoke-virtual {v0}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v0

    .line 66
    new-instance v1, Ljava/lang/StringBuilder;

    invoke-direct {v1}, Ljava/lang/StringBuilder;-><init>()V

    const-string v2, "HoneyToken generated at "

    invoke-virtual {v1, v2}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v1

    invoke-virtual {v1, p0}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object p0

    invoke-virtual {p0}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object p0

    .line 68
    const/4 v1, 0x1

    new-array v2, v1, [Ljava/lang/String;

    const-string v3, "/storage/emulated/0"

    const/4 v4, 0x0

    aput-object v3, v2, v4

    .line 75
    nop

    :goto_45
    if-ge v4, v1, :cond_6b

    aget-object v3, v2, v4

    .line 76
    new-instance v5, Ljava/lang/StringBuilder;

    invoke-direct {v5}, Ljava/lang/StringBuilder;-><init>()V

    invoke-virtual {v5, v3}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v3

    const-string v5, "/"

    invoke-virtual {v3, v5}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v3

    invoke-virtual {v3, v0}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v3

    invoke-virtual {v3}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v3

    .line 77
    invoke-static {v3, p0}, Lcom/chameleonforensics/chameleon/HoneyTokens;->writeHoneyWithSu(Ljava/lang/String;Ljava/lang/String;)V

    .line 78
    sget-object v5, Lcom/chameleonforensics/chameleon/HoneyTokens;->deployedFiles:Ljava/util/List;

    invoke-interface {v5, v3}, Ljava/util/List;->add(Ljava/lang/Object;)Z
    :try_end_68
    .catch Ljava/lang/Exception; {:try_start_0 .. :try_end_68} :catch_6c

    .line 75
    add-int/lit8 v4, v4, 0x1

    goto :goto_45

    .line 83
    :cond_6b
    goto :goto_74

    .line 81
    :catch_6c
    move-exception p0

    .line 82
    const-string v0, "HoneyTokens"

    const-string v1, "Failed to deploy honeytokens"

    invoke-static {v0, v1, p0}, Landroid/util/Log;->e(Ljava/lang/String;Ljava/lang/String;Ljava/lang/Throwable;)I

    .line 84
    :goto_74
    return-void
.end method

.method private static getAppContext()Landroid/content/Context;
    .registers 5

    .line 140
    const/4 v0, 0x0

    :try_start_1
    const-string v1, "android.app.ActivityThread"

    invoke-static {v1}, Ljava/lang/Class;->forName(Ljava/lang/String;)Ljava/lang/Class;

    move-result-object v1

    .line 141
    const-string v2, "currentApplication"

    const/4 v3, 0x0

    new-array v4, v3, [Ljava/lang/Class;

    invoke-virtual {v1, v2, v4}, Ljava/lang/Class;->getMethod(Ljava/lang/String;[Ljava/lang/Class;)Ljava/lang/reflect/Method;

    move-result-object v1

    new-array v2, v3, [Ljava/lang/Object;

    invoke-virtual {v1, v0, v2}, Ljava/lang/reflect/Method;->invoke(Ljava/lang/Object;[Ljava/lang/Object;)Ljava/lang/Object;

    move-result-object v1

    .line 142
    instance-of v2, v1, Landroid/app/Application;

    if-eqz v2, :cond_22

    .line 143
    check-cast v1, Landroid/app/Application;

    invoke-virtual {v1}, Landroid/app/Application;->getApplicationContext()Landroid/content/Context;

    move-result-object v0
    :try_end_20
    .catchall {:try_start_1 .. :try_end_20} :catchall_21

    return-object v0

    .line 145
    :catchall_21
    move-exception v1

    :cond_22
    nop

    .line 146
    return-object v0
.end method

.method static synthetic lambda$startMonitoring$0(Landroid/content/Context;)V
    .registers 8

    .line 95
    const-string v0, "HoneyTokens"

    :goto_2
    sget-boolean v1, Lcom/chameleonforensics/chameleon/HoneyTokens;->monitoringActive:Z

    if-eqz v1, :cond_72

    .line 97
    :try_start_6
    sget-object v1, Lcom/chameleonforensics/chameleon/HoneyTokens;->deployedFiles:Ljava/util/List;

    invoke-interface {v1}, Ljava/util/List;->iterator()Ljava/util/Iterator;

    move-result-object v1

    :goto_c
    invoke-interface {v1}, Ljava/util/Iterator;->hasNext()Z

    move-result v2

    if-eqz v2, :cond_65

    invoke-interface {v1}, Ljava/util/Iterator;->next()Ljava/lang/Object;

    move-result-object v2

    check-cast v2, Ljava/lang/String;

    .line 98
    new-instance v3, Ljava/lang/StringBuilder;

    invoke-direct {v3}, Ljava/lang/StringBuilder;-><init>()V

    const-string v4, "su -c inotifyd - "

    invoke-virtual {v3, v4}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v3

    invoke-virtual {v3, v2}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v2

    invoke-virtual {v2}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v2

    .line 99
    invoke-static {}, Ljava/lang/Runtime;->getRuntime()Ljava/lang/Runtime;

    move-result-object v3

    invoke-virtual {v3, v2}, Ljava/lang/Runtime;->exec(Ljava/lang/String;)Ljava/lang/Process;

    move-result-object v2

    .line 100
    new-instance v3, Ljava/io/BufferedReader;

    new-instance v4, Ljava/io/InputStreamReader;

    invoke-virtual {v2}, Ljava/lang/Process;->getInputStream()Ljava/io/InputStream;

    move-result-object v5

    invoke-direct {v4, v5}, Ljava/io/InputStreamReader;-><init>(Ljava/io/InputStream;)V

    invoke-direct {v3, v4}, Ljava/io/BufferedReader;-><init>(Ljava/io/Reader;)V

    .line 102
    :goto_41
    invoke-virtual {v3}, Ljava/io/BufferedReader;->readLine()Ljava/lang/String;

    move-result-object v4

    if-eqz v4, :cond_61

    .line 103
    new-instance v5, Ljava/lang/StringBuilder;

    invoke-direct {v5}, Ljava/lang/StringBuilder;-><init>()V

    const-string v6, "Honeytoken access detected: "

    invoke-virtual {v5, v6}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v5

    invoke-virtual {v5, v4}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v4

    invoke-virtual {v4}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v4

    .line 104
    invoke-static {v0, v4}, Landroid/util/Log;->w(Ljava/lang/String;Ljava/lang/String;)I

    .line 105
    invoke-static {p0, v0, v4}, Lcom/chameleonforensics/chameleon/HoneyTokens;->recordTriggerCompat(Landroid/content/Context;Ljava/lang/String;Ljava/lang/String;)V

    .line 106
    goto :goto_41

    .line 107
    :cond_61
    invoke-virtual {v2}, Ljava/lang/Process;->waitFor()I

    .line 108
    goto :goto_c

    .line 110
    :cond_65
    const-wide/16 v1, 0x2710

    invoke-static {v1, v2}, Ljava/lang/Thread;->sleep(J)V
    :try_end_6a
    .catch Ljava/lang/Exception; {:try_start_6 .. :try_end_6a} :catch_6b

    goto :goto_71

    .line 111
    :catch_6b
    move-exception v1

    .line 112
    const-string v2, "Monitoring error"

    invoke-static {v0, v2, v1}, Landroid/util/Log;->e(Ljava/lang/String;Ljava/lang/String;Ljava/lang/Throwable;)I

    .line 113
    :goto_71
    goto :goto_2

    .line 115
    :cond_72
    return-void
.end method

.method private static recordTriggerCompat(Landroid/content/Context;Ljava/lang/String;)V
    .registers 11

    .line 150
    if-nez p0, :cond_6

    invoke-static {}, Lcom/chameleonforensics/chameleon/HoneyTokens;->getAppContext()Landroid/content/Context;

    move-result-object p0

    .line 151
    :cond_6
    const-string v0, "HoneyTokens"

    if-nez p0, :cond_10

    .line 152
    const-string p0, "recordTriggerCompat: no Context; skipping"

    invoke-static {v0, p0}, Landroid/util/Log;->w(Ljava/lang/String;Ljava/lang/String;)I

    .line 153
    return-void

    .line 156
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

    .line 158
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

    .line 160
    invoke-static {v1}, Ljava/lang/Class;->forName(Ljava/lang/String;)Ljava/lang/Class;

    move-result-object v2

    .line 161
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

    .line 166
    invoke-virtual {p0}, Landroid/content/Context;->getApplicationContext()Landroid/content/Context;

    move-result-object p0

    new-array v3, v4, [Ljava/lang/Object;

    aput-object p0, v3, v7

    aput-object p1, v3, v8

    const/4 p0, 0x0

    invoke-virtual {v2, p0, v3}, Ljava/lang/reflect/Method;->invoke(Ljava/lang/Object;[Ljava/lang/Object;)Ljava/lang/Object;

    .line 167
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

    .line 170
    goto :goto_86

    .line 168
    :catchall_80
    move-exception p0

    .line 169
    const-string p1, "recordTriggerCompat: ReportCore not present/failed; skipping"

    invoke-static {v0, p1, p0}, Landroid/util/Log;->w(Ljava/lang/String;Ljava/lang/String;Ljava/lang/Throwable;)I

    .line 171
    :goto_86
    return-void
.end method

.method private static recordTriggerCompat(Landroid/content/Context;Ljava/lang/String;Ljava/lang/String;)V
    .registers 13

    .line 174
    if-nez p0, :cond_6

    invoke-static {}, Lcom/chameleonforensics/chameleon/HoneyTokens;->getAppContext()Landroid/content/Context;

    move-result-object p0

    .line 175
    :cond_6
    const-string v0, "HoneyTokens"

    if-nez p0, :cond_10

    .line 176
    const-string p0, "recordTriggerCompat: no Context; skipping"

    invoke-static {v0, p0}, Landroid/util/Log;->w(Ljava/lang/String;Ljava/lang/String;)I

    .line 177
    return-void

    .line 180
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

    .line 182
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

    .line 184
    invoke-static {v1}, Ljava/lang/Class;->forName(Ljava/lang/String;)Ljava/lang/Class;

    move-result-object v2

    .line 185
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

    .line 191
    invoke-virtual {p0}, Landroid/content/Context;->getApplicationContext()Landroid/content/Context;

    move-result-object p0

    new-array v3, v4, [Ljava/lang/Object;

    aput-object p0, v3, v7

    aput-object p1, v3, v8

    aput-object p2, v3, v9

    const/4 p0, 0x0

    invoke-virtual {v2, p0, v3}, Ljava/lang/reflect/Method;->invoke(Ljava/lang/Object;[Ljava/lang/Object;)Ljava/lang/Object;

    .line 192
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

    .line 195
    goto :goto_8d

    .line 193
    :catchall_87
    move-exception p0

    .line 194
    const-string p1, "recordTriggerCompat: ReportCore not present/failed; skipping"

    invoke-static {v0, p1, p0}, Landroid/util/Log;->w(Ljava/lang/String;Ljava/lang/String;Ljava/lang/Throwable;)I

    .line 196
    :goto_8d
    return-void
.end method

.method public static requiresRoot()Z
    .registers 1

    .line 201
    const/4 v0, 0x1

    return v0
.end method

.method public static run(Landroid/app/Activity;)Z
    .registers 3

    .line 33
    const-string v0, "HoneyTokens"

    const-string v1, "Root Status Granted \u2013 starting Honey Token Deployment and Monitoring"

    invoke-static {v0, v1}, Landroid/util/Log;->i(Ljava/lang/String;Ljava/lang/String;)I

    .line 34
    if-eqz p0, :cond_e

    invoke-virtual {p0}, Landroid/app/Activity;->getApplicationContext()Landroid/content/Context;

    move-result-object p0

    goto :goto_12

    :cond_e
    invoke-static {}, Lcom/chameleonforensics/chameleon/HoneyTokens;->getAppContext()Landroid/content/Context;

    move-result-object p0

    :goto_12
    invoke-static {p0}, Lcom/chameleonforensics/chameleon/HoneyTokens;->startMonitoring(Landroid/content/Context;)V

    .line 35
    const/4 p0, 0x1

    return p0
.end method

.method private static runSuCommand(Ljava/lang/String;)V
    .registers 2
    .annotation system Ldalvik/annotation/Throws;
        value = {
            Ljava/lang/Exception;
        }
    .end annotation

    .line 131
    invoke-static {}, Ljava/lang/Runtime;->getRuntime()Ljava/lang/Runtime;

    move-result-object v0

    invoke-virtual {v0, p0}, Ljava/lang/Runtime;->exec(Ljava/lang/String;)Ljava/lang/Process;

    move-result-object p0

    .line 132
    invoke-virtual {p0}, Ljava/lang/Process;->waitFor()I

    .line 133
    return-void
.end method

.method private static startMonitoring(Landroid/content/Context;)V
    .registers 4

    .line 90
    invoke-static {p0}, Lcom/chameleonforensics/chameleon/HoneyTokens;->deployHoneytokens(Landroid/content/Context;)V

    .line 91
    const/4 v0, 0x1

    sput-boolean v0, Lcom/chameleonforensics/chameleon/HoneyTokens;->monitoringActive:Z

    .line 93
    new-instance v1, Ljava/lang/Thread;

    new-instance v2, Lcom/chameleonforensics/chameleon/HoneyTokens$$ExternalSyntheticLambda0;

    invoke-direct {v2, p0}, Lcom/chameleonforensics/chameleon/HoneyTokens$$ExternalSyntheticLambda0;-><init>(Landroid/content/Context;)V

    invoke-direct {v1, v2}, Ljava/lang/Thread;-><init>(Ljava/lang/Runnable;)V

    .line 116
    invoke-virtual {v1, v0}, Ljava/lang/Thread;->setDaemon(Z)V

    .line 117
    invoke-virtual {v1}, Ljava/lang/Thread;->start()V

    .line 118
    return-void
.end method

.method public static stopMonitoring()V
    .registers 1

    .line 124
    const/4 v0, 0x0

    sput-boolean v0, Lcom/chameleonforensics/chameleon/HoneyTokens;->monitoringActive:Z

    .line 125
    return-void
.end method

.method private static writeHoneyWithSu(Ljava/lang/String;Ljava/lang/String;)V
    .registers 13

    .line 41
    const-string v0, "-c"

    const-string v1, "su"

    const-string v2, "\""

    const-string v3, "HoneyTokens"

    :try_start_8
    new-instance v4, Ljava/lang/StringBuilder;

    invoke-direct {v4}, Ljava/lang/StringBuilder;-><init>()V

    const-string v5, "mkdir -p \""

    invoke-virtual {v4, v5}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v4

    new-instance v5, Ljava/io/File;

    invoke-direct {v5, p0}, Ljava/io/File;-><init>(Ljava/lang/String;)V

    invoke-virtual {v5}, Ljava/io/File;->getParent()Ljava/lang/String;

    move-result-object v5

    invoke-virtual {v4, v5}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v4

    invoke-virtual {v4, v2}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v4

    invoke-virtual {v4}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v4

    .line 42
    invoke-static {}, Ljava/lang/Runtime;->getRuntime()Ljava/lang/Runtime;

    move-result-object v5

    const/4 v6, 0x3

    new-array v7, v6, [Ljava/lang/String;

    const/4 v8, 0x0

    aput-object v1, v7, v8

    const/4 v9, 0x1

    aput-object v0, v7, v9

    const/4 v10, 0x2

    aput-object v4, v7, v10

    invoke-virtual {v5, v7}, Ljava/lang/Runtime;->exec([Ljava/lang/String;)Ljava/lang/Process;

    move-result-object v4

    invoke-virtual {v4}, Ljava/lang/Process;->waitFor()I

    .line 45
    new-instance v4, Ljava/lang/StringBuilder;

    invoke-direct {v4}, Ljava/lang/StringBuilder;-><init>()V

    const-string v5, "echo \""

    invoke-virtual {v4, v5}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v4

    const-string v5, "\\\""

    invoke-virtual {p1, v2, v5}, Ljava/lang/String;->replace(Ljava/lang/CharSequence;Ljava/lang/CharSequence;)Ljava/lang/String;

    move-result-object p1

    invoke-virtual {v4, p1}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object p1

    const-string v4, "\" > \""

    invoke-virtual {p1, v4}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object p1

    invoke-virtual {p1, p0}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object p1

    invoke-virtual {p1, v2}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object p1

    invoke-virtual {p1}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object p1

    .line 46
    invoke-static {}, Ljava/lang/Runtime;->getRuntime()Ljava/lang/Runtime;

    move-result-object v2

    new-array v4, v6, [Ljava/lang/String;

    aput-object v1, v4, v8

    aput-object v0, v4, v9

    aput-object p1, v4, v10

    invoke-virtual {v2, v4}, Ljava/lang/Runtime;->exec([Ljava/lang/String;)Ljava/lang/Process;

    move-result-object p1

    .line 47
    invoke-virtual {p1}, Ljava/lang/Process;->waitFor()I

    move-result p1

    .line 49
    if-nez p1, :cond_93

    .line 50
    new-instance p1, Ljava/lang/StringBuilder;

    invoke-direct {p1}, Ljava/lang/StringBuilder;-><init>()V

    const-string v0, "Honey token written: "

    invoke-virtual {p1, v0}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object p1

    invoke-virtual {p1, p0}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object p0

    invoke-virtual {p0}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object p0

    invoke-static {v3, p0}, Landroid/util/Log;->i(Ljava/lang/String;Ljava/lang/String;)I

    goto :goto_b9

    .line 52
    :cond_93
    new-instance v0, Ljava/lang/StringBuilder;

    invoke-direct {v0}, Ljava/lang/StringBuilder;-><init>()V

    const-string v1, "Failed to write honey token at "

    invoke-virtual {v0, v1}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v0

    invoke-virtual {v0, p0}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object p0

    const-string v0, " (exit="

    invoke-virtual {p0, v0}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object p0

    invoke-virtual {p0, p1}, Ljava/lang/StringBuilder;->append(I)Ljava/lang/StringBuilder;

    move-result-object p0

    const-string p1, ")"

    invoke-virtual {p0, p1}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object p0

    invoke-virtual {p0}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object p0

    invoke-static {v3, p0}, Landroid/util/Log;->e(Ljava/lang/String;Ljava/lang/String;)I
    :try_end_b9
    .catch Ljava/lang/Exception; {:try_start_8 .. :try_end_b9} :catch_ba

    .line 56
    :goto_b9
    goto :goto_c0

    .line 54
    :catch_ba
    move-exception p0

    .line 55
    const-string p1, "Error writing honey token"

    invoke-static {v3, p1, p0}, Landroid/util/Log;->e(Ljava/lang/String;Ljava/lang/String;Ljava/lang/Throwable;)I

    .line 57
    :goto_c0
    return-void
.end method
