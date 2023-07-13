import torch


def train(
    model,
    device,
    train_loader,
    criterion,
    optimizer,
    epoch,
    train_loss,
    train_acc,
    mse,
):
    model.train()
    curr_loss = 0
    t_pred = 0

    for batch_idx, (images_1, targets) in enumerate(train_loader):
        images_1, targets = images_1.to(device), targets.to(device)
        optimizer.zero_grad()
        output1, recons = model(images_1)
        loss_m = criterion(output1, targets)
        vae = mse(recons, images_1)
        loss = loss_m + vae  # +model.encoder.kl

        loss.backward()
        optimizer.step()

        curr_loss += loss.sum().item()
        _, preds = torch.max(output1, 1)
        t_pred += torch.sum(preds == targets.data).item()

        if batch_idx % 10 == 0:
            print(
                "Train Epoch: {} [{}/{} ({:.0f}%)]\tLoss: {:.6f} vae_Loss {:.6f}".format(
                    epoch,
                    batch_idx * len(images_1),
                    len(train_loader.dataset),
                    100.0 * batch_idx / len(train_loader),
                    loss_m.item(),
                    vae.item(),
                )
            )

            train_loss.append(loss.sum().item() / len(images_1))
            train_acc.append(preds.sum().item() / len(images_1))
    epoch_loss = curr_loss / len(train_loader.dataset)
    epoch_acc = t_pred / len(train_loader.dataset)

    train_loss.append(epoch_loss)
    train_acc.append(epoch_acc)

    print(
        "\nTrain set: Average loss: {:.4f}, Accuracy: {}/{} ({:.0f}%)\n".format(
            epoch_loss,
            t_pred,
            len(train_loader.dataset),
            100.0 * t_pred / len(train_loader.dataset),
        )
    )

    return train_loss, train_acc, epoch_loss


def valid(model, device, test_loader, criterion, epoch, valid_loss, valid_acc, mse):
    model.eval()
    test_loss = 0
    correct = 0

    with torch.no_grad():
        for batch_idx, (images_1, targets) in enumerate(test_loader):
            images_1, targets = images_1.to(device), targets.to(device)
            output1, recons = model(images_1)
            loss_m = criterion(output1, targets)
            vae = mse(recons, images_1)
            loss = loss_m + vae  # +model.encoder.kl

            test_loss += loss.sum().item()  # sum up batch loss

            _, preds = torch.max(output1, 1)
            correct += torch.sum(preds == targets.data)

            if batch_idx % 10 == 0:
                print(
                    "Test Epoch: {} [{}/{} ({:.0f}%)]\tLoss: {:.6f} vae_Loss {:.6f}".format(
                        epoch,
                        batch_idx * len(images_1),
                        len(test_loader.dataset),
                        100.0 * batch_idx / len(test_loader),
                        loss_m.item(),
                        vae.item(),
                    )
                )

                valid_loss.append(loss.sum().item() / len(images_1))
                valid_acc.append(preds.sum().item() / len(images_1))

    epoch_loss = test_loss / len(test_loader.dataset)
    epoch_acc = correct / len(test_loader.dataset)

    valid_loss.append(epoch_loss)
    valid_acc.append(epoch_acc.item())

    print(
        "\nTest set: Average loss: {:.4f}, Accuracy: {}/{} ({:.0f}%)\n".format(
            epoch_loss,
            correct,
            len(test_loader.dataset),
            100.0 * correct / len(test_loader.dataset),
        )
    )

    return valid_loss, valid_acc