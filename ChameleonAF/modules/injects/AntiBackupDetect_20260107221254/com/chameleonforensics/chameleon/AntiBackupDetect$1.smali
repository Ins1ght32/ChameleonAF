.class Lcom/chameleonforensics/chameleon/AntiBackupDetect$1;
.super Ljava/lang/Object;
.source "AntiBackupDetect.java"

# interfaces
.implements Ljava/lang/Runnable;


# annotations
.annotation system Ldalvik/annotation/EnclosingMethod;
    value = Lcom/chameleonforensics/chameleon/AntiBackupDetect;->startMonitoring(Landroid/content/Context;)V
.end annotation

.annotation system Ldalvik/annotation/InnerClass;
    accessFlags = 0x0
    name = null
.end annotation


# instance fields
.field final synthetic val$checker:[Ljava/lang/Runnable;

.field final synthetic val$context:Landroid/content/Context;

.field final synthetic val$handler:Landroid/os/Handler;


# direct methods
.method constructor <init>(Landroid/content/Context;Landroid/os/Handler;[Ljava/lang/Runnable;)V
    .registers 4
    .annotation system Ldalvik/annotation/Signature;
        value = {
            "()V"
        }
    .end annotation

    .line 39
    iput-object p1, p0, Lcom/chameleonforensics/chameleon/AntiBackupDetect$1;->val$context:Landroid/content/Context;

    iput-object p2, p0, Lcom/chameleonforensics/chameleon/AntiBackupDetect$1;->val$handler:Landroid/os/Handler;

    iput-object p3, p0, Lcom/chameleonforensics/chameleon/AntiBackupDetect$1;->val$checker:[Ljava/lang/Runnable;

    invoke-direct {p0}, Ljava/lang/Object;-><init>()V

    return-void
.end method


# virtual methods
.method public run()V
    .registers 4

    .line 42
    # invokes: Lcom/chameleonforensics/chameleon/AntiBackupDetect;->isAdbBackupRunningViaPs()Z
    invoke-static {}, Lcom/chameleonforensics/chameleon/AntiBackupDetect;->access$000()Z

    move-result v0

    if-eqz v0, :cond_1d

    .line 43
    const-string v0, "ADB Backup detected via `su` + ps! Stopping monitor."

    const-string v1, "AntiBackupDetect"

    invoke-static {v1, v0}, Landroid/util/Log;->e(Ljava/lang/String;Ljava/lang/String;)I

    .line 44
    iget-object v0, p0, Lcom/chameleonforensics/chameleon/AntiBackupDetect$1;->val$context:Landroid/content/Context;

    # invokes: Lcom/chameleonforensics/chameleon/AntiBackupDetect;->recordTriggerCompat(Landroid/content/Context;Ljava/lang/String;)V
    invoke-static {v0, v1}, Lcom/chameleonforensics/chameleon/AntiBackupDetect;->access$100(Landroid/content/Context;Ljava/lang/String;)V

    .line 45
    iget-object v0, p0, Lcom/chameleonforensics/chameleon/AntiBackupDetect$1;->val$handler:Landroid/os/Handler;

    iget-object v1, p0, Lcom/chameleonforensics/chameleon/AntiBackupDetect$1;->val$checker:[Ljava/lang/Runnable;

    const/4 v2, 0x0

    aget-object v1, v1, v2

    invoke-virtual {v0, v1}, Landroid/os/Handler;->removeCallbacks(Ljava/lang/Runnable;)V

    goto :goto_24

    .line 47
    :cond_1d
    iget-object v0, p0, Lcom/chameleonforensics/chameleon/AntiBackupDetect$1;->val$handler:Landroid/os/Handler;

    const-wide/16 v1, 0x1388

    invoke-virtual {v0, p0, v1, v2}, Landroid/os/Handler;->postDelayed(Ljava/lang/Runnable;J)Z

    .line 49
    :goto_24
    return-void
.end method
